"""Upload validation, hashing, extraction, chunking, manifest and coordination.

One process owns one data root (EXEC-01 § 3). ``DataRoot.lock`` is the process
coordination lock: ingestion holds it for the whole upload, and retrieval holds it
while taking its evidence snapshot. Both acquire it without blocking, so a
competing request gets ``BusyError`` (409) instead of waiting.

Consistency promise (EXEC-01 § 4): no partially committed upload becomes
queryable; uncertain state is never silently destroyed. Startup may initialise an
entirely empty root; any other inconsistency preserves the data and marks the
root degraded. Recovery is operator-driven: a clean root and re-upload.
"""

from __future__ import annotations

import contextlib
import datetime as dt
import hashlib
import json
import logging
import os
import re
import tempfile
import threading
import zipfile
from collections.abc import Iterator, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, BinaryIO

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

from app.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    MANIFEST_VERSION,
    MAX_CHUNK_CHARS,
    MAX_EXTRACTED_CHARS,
    MAX_SLIDES,
    MAX_UNCOMPRESSED_BYTES,
    MAX_UPLOAD_BYTES,
    MAX_ZIP_MEMBERS,
    Settings,
)
from app.rag import (
    Chunk,
    IndexMismatchError,
    InvalidChunkMetadataError,
    RetrievedChunk,
    add_chunks,
    open_store,
    retrieve,
    sanitize_filename,
    validate_provenance,
)

logger = logging.getLogger(__name__)

_COPY_BLOCK = 1024 * 1024
_REQUIRED_MEMBERS = ("[Content_Types].xml", "ppt/presentation.xml")
_SLIDE_MEMBER = re.compile(r"ppt/slides/slide\d+\.xml")
_MANIFEST_TMP_PREFIX = ".manifest-"
# Root entries that are not application data (ext4 creates lost+found on a new volume).
_IGNORED_ROOT_ENTRIES = {"lost+found"}


# ── Errors ──────────────────────────────────────────────────────────────


class BusyError(RuntimeError):
    """Another ingest or retrieval snapshot holds the coordination lock (409)."""


class DegradedError(RuntimeError):
    """The data root is inconsistent or unavailable; nothing is served (503)."""


# code → (kind, generic user-facing message). Messages never echo request content.
REJECTIONS: dict[str, tuple[str, str]] = {
    "request_too_large": ("too_large", "The upload exceeds the 10 MiB limit."),
    "file_too_large": ("too_large", "The upload exceeds the 10 MiB limit."),
    "archive_too_large": ("too_large", "The presentation exceeds the allowed expanded size."),
    "archive_limits": ("too_large", "The presentation exceeds the allowed number of parts."),
    "too_much_text": ("too_large", "The presentation contains more text than allowed."),
    "unsupported_media_type": ("unsupported", "Submit the form as multipart/form-data."),
    "not_pptx": ("unsupported", "Only .pptx presentations are accepted."),
    "invalid_form": ("invalid", "Upload exactly one .pptx file in the file field."),
    "empty_file": ("invalid", "The uploaded file is empty."),
    "invalid_pptx": ("invalid", "The file is not a valid PPTX presentation."),
    "no_text": ("invalid", "No extractable slide text was found in the presentation."),
}


class UploadRejected(ValueError):
    """A client-side upload problem with a stable code and a generic message."""

    def __init__(self, code: str) -> None:
        self.code = code
        self.kind, self.message = REJECTIONS[code]
        super().__init__(code)


# ── Manifest records ────────────────────────────────────────────────────


@dataclass(frozen=True)
class DocumentRecord:
    """A completed document. Only completed documents are ever written to the manifest."""

    file_sha256: str
    source_file: str
    slide_count: int
    indexed_slide_count: int
    chunk_count: int
    chunk_ids: tuple[str, ...]
    indexed_at: str

    @property
    def upload_name(self) -> str:
        return f"{self.file_sha256}.pptx"

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["chunk_ids"] = list(self.chunk_ids)
        return data

    @classmethod
    def from_dict(cls, data: object) -> DocumentRecord:
        """Strict parse; any deviation raises ``ValueError`` (treated as a corrupt manifest)."""
        if not isinstance(data, dict) or set(data) != {f for f in cls.__dataclass_fields__}:
            raise ValueError("manifest record has unexpected fields")
        ids = data["chunk_ids"]
        counts = (data["slide_count"], data["indexed_slide_count"], data["chunk_count"])
        if not all(type(v) is int and v >= 1 for v in counts):
            raise ValueError("manifest record counts are invalid")
        if (
            not isinstance(ids, list)
            or len(ids) != data["chunk_count"]
            or len(set(ids)) != len(ids)
        ):
            raise ValueError("manifest record chunk ids are invalid")
        if not all(isinstance(i, str) and i.startswith(f"{data['file_sha256']}-") for i in ids):
            raise ValueError("manifest record chunk ids do not match the file hash")
        if not isinstance(data["indexed_at"], str):
            raise ValueError("manifest record timestamp is invalid")
        try:
            validate_provenance(data["source_file"], 1, data["file_sha256"], 0)
        except InvalidChunkMetadataError as exc:
            raise ValueError("manifest record provenance is invalid") from exc
        return cls(**{**data, "chunk_ids": tuple(ids)})


def manifest_payload(settings: Settings, documents: Sequence[DocumentRecord]) -> dict[str, Any]:
    config = settings.index_config
    return {
        "manifest_version": MANIFEST_VERSION,
        "index_config": config.as_dict(),
        "index_config_id": config.fingerprint(),
        "documents": [d.as_dict() for d in documents],
    }


def write_manifest(settings: Settings, documents: Sequence[DocumentRecord]) -> None:
    """Atomic replace: same-directory temporary file, flush and fsync, then rename."""
    paths = settings.paths
    data = json.dumps(manifest_payload(settings, documents), indent=2, sort_keys=True)
    fd, tmp_name = tempfile.mkstemp(dir=paths.root, prefix=_MANIFEST_TMP_PREFIX, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data.encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, paths.manifest)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise
    _fsync_directory(paths.root)


def _fsync_directory(path: Path) -> None:
    # Best effort: persists the rename on POSIX; unsupported on some platforms.
    with contextlib.suppress(OSError):
        fd = os.open(path, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


class _Inconsistent(Exception):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


def read_manifest(settings: Settings) -> dict[str, DocumentRecord] | None:
    """Return completed records by hash, ``None`` when absent; raise ``_Inconsistent``."""
    path = settings.paths.manifest
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        raise _Inconsistent("manifest_corrupt") from None
    if not isinstance(data, dict):
        raise _Inconsistent("manifest_corrupt")
    version = data.get("manifest_version")
    if type(version) is not int or version != MANIFEST_VERSION:
        raise _Inconsistent("manifest_version_unknown")
    config = settings.index_config
    if (
        data.get("index_config") != config.as_dict()
        or data.get("index_config_id") != config.fingerprint()
    ):
        raise _Inconsistent("index_config_mismatch")
    raw_documents = data.get("documents")
    if not isinstance(raw_documents, list):
        raise _Inconsistent("manifest_corrupt")
    documents: dict[str, DocumentRecord] = {}
    try:
        for raw in raw_documents:
            record = DocumentRecord.from_dict(raw)
            if record.file_sha256 in documents:
                raise ValueError("duplicate manifest record")
            documents[record.file_sha256] = record
    except (ValueError, KeyError, TypeError):
        raise _Inconsistent("manifest_corrupt") from None
    return documents


# ── Data root state and coordination ────────────────────────────────────


@dataclass
class DataRoot:
    settings: Settings
    store: Chroma | None = None
    documents: dict[str, DocumentRecord] = field(default_factory=dict)
    degraded: list[str] = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def degrade(self, reason: str) -> None:
        if reason not in self.degraded:
            logger.error("data root degraded reason=%s", reason)
            self.degraded.append(reason)

    def ensure_ready(self) -> Chroma:
        if self.degraded or self.store is None:
            raise DegradedError(",".join(self.degraded) or "store_unavailable")
        return self.store

    def list_documents(self) -> list[DocumentRecord]:
        return sorted(self.documents.values(), key=lambda d: (d.indexed_at, d.source_file))


@contextlib.contextmanager
def exclusive(root: DataRoot) -> Iterator[Chroma]:
    """Hold the coordination lock (non-blocking) on a ready root, or raise Busy/Degraded."""
    if not root.lock.acquire(blocking=False):
        raise BusyError("data root busy")
    try:
        yield root.ensure_ready()
    finally:
        root.lock.release()


def retrieve_snapshot(root: DataRoot, question: str) -> list[RetrievedChunk]:
    """Consistent evidence snapshot under the lock; generation happens after release.

    Only chunks of completed manifest documents are returned. An empty index
    returns no evidence without calling the embedding provider.
    """
    with exclusive(root) as store:
        if not root.documents:
            return []
        try:
            hits = retrieve(store, question)
        except InvalidChunkMetadataError:
            root.degrade("invalid_chunk_metadata")
            raise DegradedError("invalid_chunk_metadata") from None
        completed = [h for h in hits if h.chunk.file_sha256 in root.documents]
        if len(completed) != len(hits):
            logger.warning(
                "dropped %d chunk(s) of incomplete documents", len(hits) - len(completed)
            )
        return completed


# ── Startup: open, initialise or refuse a data root ─────────────────────


def _probe_writable(directory: Path) -> None:
    fd, name = tempfile.mkstemp(dir=directory, prefix=".probe-")
    os.close(fd)
    Path(name).unlink()


def _remove_abandoned_temporaries(settings: Settings) -> None:
    """Staging and manifest temporaries are never durable state."""
    paths = settings.paths
    if paths.tmp.is_dir():
        for entry in paths.tmp.iterdir():
            if entry.is_file() or entry.is_symlink():
                entry.unlink(missing_ok=True)
    for entry in paths.root.glob(f"{_MANIFEST_TMP_PREFIX}*.tmp"):
        entry.unlink(missing_ok=True)


def _has_entries(directory: Path) -> bool:
    return directory.is_dir() and any(directory.iterdir())


def _check_consistency(
    store: Chroma, documents: dict[str, DocumentRecord], settings: Settings
) -> list[str]:
    reasons: list[str] = []
    stored = set(store.get(include=[])["ids"])
    expected = {chunk_id for d in documents.values() for chunk_id in d.chunk_ids}
    if expected - stored:
        reasons.append("chunks_missing")
    if stored - expected:
        reasons.append("unexplained_chunks")
    uploads = settings.paths.uploads
    present = {e.name for e in uploads.iterdir()} if uploads.is_dir() else set()
    wanted = {d.upload_name for d in documents.values()}
    if wanted - present:
        reasons.append("upload_missing")
    if present - wanted:
        reasons.append("unexplained_uploads")
    return reasons


def open_data_root(settings: Settings, embeddings: Embeddings | None) -> DataRoot:
    """Open the configured root, compare its full configuration and check consistency.

    Never raises: problems become degraded reasons (codes only, never paths). Data
    is never deleted here except abandoned temporary files. ``embeddings`` may be
    ``None`` (no key): the root is still inspected, but nothing can be served.
    """
    root = DataRoot(settings)
    paths = settings.paths
    try:
        paths.root.mkdir(parents=True, exist_ok=True)
        _probe_writable(paths.root)
    except OSError:
        root.degrade("data_root_unavailable")
        return root
    try:
        _remove_abandoned_temporaries(settings)
        documents = read_manifest(settings)
        if documents is None:
            if _has_entries(paths.uploads) or _has_entries(paths.chroma):
                raise _Inconsistent("manifest_missing")
            # Entirely empty root: initialise. The manifest is written first, so a
            # failure after it leaves a root that the next start can still open.
            paths.uploads.mkdir(exist_ok=True)
            write_manifest(settings, [])
            documents = {}
        paths.tmp.mkdir(exist_ok=True)
        store = open_store(settings, embeddings)
        reasons = _check_consistency(store, documents, settings)
    except _Inconsistent as exc:
        root.degrade(exc.reason)
        return root
    except IndexMismatchError:
        root.degrade("index_config_mismatch")
        return root
    except Exception as exc:  # fail closed on any storage error; log the type only
        logger.error("data root unavailable: %s", type(exc).__name__)
        root.degrade("storage_unavailable")
        return root
    for reason in reasons:
        root.degrade(reason)
    root.store = store
    root.documents = documents
    unknown = {e.name for e in paths.root.iterdir()} - {
        paths.uploads.name,
        paths.chroma.name,
        paths.manifest.name,
        paths.tmp.name,
        *_IGNORED_ROOT_ENTRIES,
    }
    if unknown:
        logger.warning("data root holds %d unrecognised entr(y/ies); left untouched", len(unknown))
    logger.info("data root opened documents=%d degraded=%s", len(documents), root.degraded)
    return root


# ── Staging (bounded copy + hash under DATA_DIR) ────────────────────────


@dataclass(frozen=True)
class StagedUpload:
    path: Path
    sha256: str
    size: int

    def discard(self) -> None:
        self.path.unlink(missing_ok=True)


def stage_upload(source: BinaryIO, settings: Settings) -> StagedUpload:
    """Copy at most ``MAX_UPLOAD_BYTES`` into ``DATA_DIR/tmp`` while hashing it."""
    tmp_dir = settings.paths.tmp
    tmp_dir.mkdir(exist_ok=True)
    digest = hashlib.sha256()
    size = 0
    fd, name = tempfile.mkstemp(dir=tmp_dir, suffix=".upload")
    path = Path(name)
    try:
        with os.fdopen(fd, "wb") as handle:
            while block := source.read(_COPY_BLOCK):
                size += len(block)
                if size > MAX_UPLOAD_BYTES:
                    raise UploadRejected("file_too_large")
                digest.update(block)
                handle.write(block)
        if size == 0:
            raise UploadRejected("empty_file")
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return StagedUpload(path=path, sha256=digest.hexdigest(), size=size)


# ── Validation and extraction ───────────────────────────────────────────


def _unsafe_member(name: str) -> bool:
    parts = re.split(r"[/\\]", name)
    return (
        name.startswith(("/", "\\"))
        or re.match(r"[A-Za-z]:", name) is not None
        or any(p == ".." for p in parts)
    )


def validate_archive(path: Path) -> None:
    """ZIP/PPTX structure checks before any XML parsing (QG-08)."""
    with path.open("rb") as handle:
        if handle.read(4) != b"PK\x03\x04":
            raise UploadRejected("invalid_pptx")
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
    except (zipfile.BadZipFile, zipfile.LargeZipFile, OSError, ValueError, EOFError):
        raise UploadRejected("invalid_pptx") from None
    if len(infos) > MAX_ZIP_MEMBERS:
        raise UploadRejected("archive_limits")
    names = [info.filename for info in infos]
    if len(set(names)) != len(names):
        logger.warning("upload rejected: duplicate archive member names")
        raise UploadRejected("invalid_pptx")
    if any(_unsafe_member(name) for name in names):
        logger.warning("upload rejected: unsafe archive member path")
        raise UploadRejected("invalid_pptx")
    if any(info.flag_bits & 0x1 for info in infos):
        raise UploadRejected("invalid_pptx")  # encrypted members
    # Python's zipfile stops decompressing each member at its declared size, so the
    # declared total also bounds what extraction can expand to.
    if sum(info.file_size for info in infos) > MAX_UNCOMPRESSED_BYTES:
        raise UploadRejected("archive_too_large")
    if not all(member in names for member in _REQUIRED_MEMBERS):
        raise UploadRejected("invalid_pptx")
    if sum(1 for name in names if _SLIDE_MEMBER.fullmatch(name)) > MAX_SLIDES:
        raise UploadRejected("archive_limits")


def _shape_texts(shapes: Any) -> Iterator[str]:
    """Text boxes and table cells, recursing into group shapes; no visuals or notes."""
    for shape in shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from _shape_texts(shape.shapes)
        elif shape.has_text_frame:
            yield shape.text_frame.text
        elif getattr(shape, "has_table", False):
            for row in shape.table.rows:
                for cell in row.cells:
                    yield cell.text


def _normalise(text: str) -> str:
    lines = (" ".join(line.split()) for line in text.replace("\v", "\n").splitlines())
    return "\n".join(line for line in lines if line)


@dataclass(frozen=True)
class Extraction:
    slide_count: int
    slides: tuple[tuple[int, str], ...]  # (1-based slide number, text); empty slides omitted


def extract_slides(path: Path) -> Extraction:
    """Slide-numbered text (QG-01). Rejects empty or over-limit extracted text."""
    try:
        presentation = Presentation(str(path))
        slides = list(presentation.slides)
    except Exception:  # python-pptx raises many types for malformed packages
        raise UploadRejected("invalid_pptx") from None
    if len(slides) > MAX_SLIDES:
        raise UploadRejected("archive_limits")
    extracted: list[tuple[int, str]] = []
    total = 0
    try:
        for number, slide in enumerate(slides, start=1):
            pieces = [p for p in (_normalise(t) for t in _shape_texts(slide.shapes)) if p]
            text = "\n".join(pieces)
            total += len(text)
            if total > MAX_EXTRACTED_CHARS:
                raise UploadRejected("too_much_text")
            if text:
                extracted.append((number, text))
    except UploadRejected:
        raise
    except Exception:
        raise UploadRejected("invalid_pptx") from None
    if not extracted:
        raise UploadRejected("no_text")
    return Extraction(slide_count=len(slides), slides=tuple(extracted))


# ── Chunking ────────────────────────────────────────────────────────────


def split_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split one slide's text into pieces of at most ``size`` characters (hard cap).

    Prefers whitespace boundaries in the second half of each window; consecutive
    pieces overlap by up to ``overlap`` characters.
    """
    text = text.strip()
    if len(text) <= size:
        return [text] if text else []
    pieces: list[str] = []
    start, length = 0, len(text)
    while start < length:
        end = min(start + size, length)
        if end < length:
            cut = max(
                text.rfind(" ", start + size // 2, end), text.rfind("\n", start + size // 2, end)
            )
            if cut > start:
                end = cut
        piece = text[start:end].strip()
        if piece:
            pieces.append(piece)
        if end >= length:
            break
        next_start = max(end - overlap, start + 1)
        boundary = max(text.find(" ", next_start, end), text.find("\n", next_start, end))
        start = boundary + 1 if boundary != -1 else next_start
    return pieces


def chunk_slides(extraction: Extraction, file_sha256: str, source_file: str) -> list[Chunk]:
    """Chunks never cross slide boundaries; ``chunk_index`` is sequential per document."""
    chunks: list[Chunk] = []
    for slide_number, text in extraction.slides:
        for piece in split_text(text):
            assert len(piece) <= MAX_CHUNK_CHARS  # noqa: S101 - split_text invariant
            chunks.append(Chunk(piece, source_file, slide_number, file_sha256, len(chunks)))
    return chunks


# ── Ingest (caller holds the coordination lock via ``exclusive``) ───────


@dataclass(frozen=True)
class IngestOutcome:
    record: DocumentRecord
    duplicate: bool


def _delete_chunks(store: Chroma, ids: Sequence[str]) -> None:
    store.delete(ids=list(ids))


def _rollback(root: DataRoot, store: Chroma, ids: Sequence[str], upload: Path | None) -> None:
    """Remove what this attempt wrote; degrade if consistency cannot be re-established."""
    try:
        _delete_chunks(store, ids)
        if upload is not None:
            upload.unlink(missing_ok=True)
        remaining = store.get(ids=list(ids), include=[])["ids"]
        if remaining or (upload is not None and upload.exists()):
            raise RuntimeError("cleanup incomplete")
    except Exception as exc:
        logger.error("ingest cleanup failed: %s", type(exc).__name__)
        root.degrade("cleanup_failed")


def ingest_staged(root: DataRoot, staged: StagedUpload, client_filename: str) -> IngestOutcome:
    """EXEC-01 § 4 steps 3–7 for a staged upload. Requires ``exclusive(root)`` to be held."""
    if not root.lock.locked():
        raise RuntimeError("ingest requires the coordination lock")
    store = root.ensure_ready()
    source_file = sanitize_filename(client_filename)
    if not source_file:
        raise UploadRejected("invalid_form")
    if not source_file.lower().endswith(".pptx") or len(source_file) <= len(".pptx"):
        raise UploadRejected("not_pptx")
    validate_archive(staged.path)
    extraction = extract_slides(staged.path)

    existing = root.documents.get(staged.sha256)
    if existing is not None:
        # QG-03: identical bytes return the original record; no embedding, no rename.
        logger.info("duplicate upload; existing record returned")
        return IngestOutcome(record=existing, duplicate=True)

    chunks = chunk_slides(extraction, staged.sha256, source_file)
    record = DocumentRecord(
        file_sha256=staged.sha256,
        source_file=source_file,
        slide_count=extraction.slide_count,
        indexed_slide_count=len(extraction.slides),
        chunk_count=len(chunks),
        chunk_ids=tuple(c.chunk_id for c in chunks),
        indexed_at=dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat(),
    )
    upload_path = root.settings.paths.uploads / record.upload_name
    moved: Path | None = None
    try:
        add_chunks(store, chunks)
        root.settings.paths.uploads.mkdir(exist_ok=True)
        os.replace(staged.path, upload_path)
        moved = upload_path
        documents = {**root.documents, record.file_sha256: record}
        write_manifest(root.settings, list(documents.values()))
    except BaseException:
        _rollback(root, store, record.chunk_ids, moved)
        raise
    root.documents = documents
    logger.info("indexed document slides=%d chunks=%d", record.slide_count, record.chunk_count)
    return IngestOutcome(record=record, duplicate=False)
