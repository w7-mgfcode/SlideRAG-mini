"""Ingestion tests (offline; deterministic fake embeddings, temp data roots).

Mocked evidence only: these prove the ingestion contract against fakes, not real
embedding behavior. Deeper failure injection/concurrency/recovery is #13.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
import textwrap
import zipfile
from pathlib import Path

import chromadb
import pytest
from chromadb.config import Settings as ChromaSettings

from app import ingestion
from app.config import CHUNK_OVERLAP, CHUNK_SIZE, COLLECTION_NAME, MAX_CHUNK_CHARS
from app.ingestion import (
    BusyError,
    DegradedError,
    UploadRejected,
    chunk_slides,
    exclusive,
    extract_slides,
    ingest_staged,
    open_data_root,
    retrieve_snapshot,
    split_text,
    stage_upload,
)
from app.rag import ProviderError, validate_provenance
from conftest import NETWORK_GUARD_SRC, TEST_PLACEHOLDER_KEY, HashEmbeddings, make_pptx
from demo.generate_pptx import BANNER, NOTES_MARKER

SHA = "b" * 64


@pytest.fixture
def root(make_settings, fake_embeddings):
    opened = open_data_root(make_settings(key=TEST_PLACEHOLDER_KEY), fake_embeddings)
    assert opened.degraded == []
    return opened


def ingest(root, path: Path, filename: str | None = None):
    with path.open("rb") as handle, exclusive(root):
        staged = stage_upload(handle, root.settings)
        try:
            return ingest_staged(root, staged, filename or path.name)
        finally:
            staged.discard()


def stored_ids(data_dir: Path) -> list[str]:
    client = chromadb.PersistentClient(
        path=str(data_dir / "chroma"), settings=ChromaSettings(anonymized_telemetry=False)
    )
    return sorted(client.get_collection(COLLECTION_NAME).get(include=[])["ids"])


def durable_state(data_dir: Path) -> tuple[object, ...]:
    manifest = data_dir / "manifest.json"
    uploads = data_dir / "uploads"
    files = (
        sorted((p.name, hashlib.sha256(p.read_bytes()).hexdigest()) for p in uploads.iterdir())
        if uploads.is_dir()
        else []
    )
    return (manifest.read_bytes() if manifest.exists() else None, files, stored_ids(data_dir))


def manifest_documents(data_dir: Path) -> list[dict]:
    return json.loads((data_dir / "manifest.json").read_text())["documents"]


# ── QG-01 / QG-02: extraction and chunk metadata ─────────────────────────


def test_extract_slides_demo_deck_recovers_text_and_slide_numbers(demo_deck: Path) -> None:
    extraction = extract_slides(demo_deck)
    slides = dict(extraction.slides)
    assert extraction.slide_count == 10
    assert sorted(slides) == list(range(1, 11))
    assert all(BANNER in text for text in slides.values())
    assert "18 ms" in slides[4] and "46 ms" in slides[4] and "INC-042" in slides[4]
    assert "92%" in slides[5] and "85%" in slides[5]
    assert "Backhaul saturation" in slides[7] or "backhaul saturation" in slides[7]
    assert "Validate traffic volume" in slides[8] and "alarms" in slides[8]
    assert "Capacity balancing" in slides[9]
    assert "99.95%" in slides[3]  # table cell
    assert "Transport (backhaul)" in slides[2]  # text box inside a group shape
    assert all(NOTES_MARKER not in text for text in slides.values())  # notes excluded


def test_chunk_slides_preserve_valid_metadata(demo_deck: Path) -> None:
    extraction = extract_slides(demo_deck)
    chunks = chunk_slides(extraction, SHA, "5G_RAN_Operations_Demo.pptx")
    assert chunks
    assert [c.chunk_index for c in chunks] == list(range(len(chunks)))
    assert len({c.chunk_id for c in chunks}) == len(chunks)
    slide_text = dict(extraction.slides)
    for chunk in chunks:
        validate_provenance(
            chunk.source_file, chunk.slide_number, chunk.file_sha256, chunk.chunk_index
        )
        assert 0 < len(chunk.text) <= MAX_CHUNK_CHARS
        assert chunk.text in slide_text[chunk.slide_number]  # never crosses slides
    assert {c.slide_number for c in chunks} == set(range(1, 11))


def test_split_text_enforces_hard_cap_with_overlap() -> None:
    words = " ".join(f"word{i:04d}" for i in range(900))  # ~8,100 characters
    pieces = split_text(words)
    assert len(pieces) > 1
    assert all(len(p) <= CHUNK_SIZE for p in pieces)
    for first, second in zip(pieces, pieces[1:], strict=False):
        assert first.split()[-1] in second  # consecutive pieces overlap
    assert set(words.split()) == {w for p in pieces for w in p.split()}
    unbroken = "x" * (3 * CHUNK_SIZE + 7)  # no whitespace at all
    pieces = split_text(unbroken)
    assert all(len(p) <= CHUNK_SIZE for p in pieces)
    assert sum(len(p) for p in pieces) >= len(unbroken)
    assert CHUNK_OVERLAP < CHUNK_SIZE // 2
    assert split_text("   ") == []


# ── Ingest, duplicate and persistence ───────────────────────────────────


def test_ingest_demo_deck_indexes_and_records_manifest(root, demo_deck: Path, data_dir) -> None:
    outcome = ingest(root, demo_deck)
    record = outcome.record
    assert outcome.duplicate is False
    assert record.source_file == "5G_RAN_Operations_Demo.pptx"
    assert record.slide_count == 10 and record.chunk_count == len(record.chunk_ids)
    assert record.file_sha256 == hashlib.sha256(demo_deck.read_bytes()).hexdigest()
    assert stored_ids(data_dir) == sorted(record.chunk_ids)
    assert (data_dir / "uploads" / f"{record.file_sha256}.pptx").read_bytes() == (
        demo_deck.read_bytes()
    )
    manifest = json.loads((data_dir / "manifest.json").read_text())
    assert manifest["index_config_id"] == root.settings.index_config.fingerprint()
    assert manifest["documents"] == [record.as_dict()]
    assert list((data_dir / "tmp").iterdir()) == []


def test_duplicate_upload_returns_original_record_without_embedding(
    root, demo_deck: Path, data_dir, fake_embeddings
) -> None:
    """QG-03 / Sourcery #9, #15: same bytes under a new name: no embedding, no change."""
    first = ingest(root, demo_deck).record
    calls_after_first = fake_embeddings.document_calls
    before = durable_state(data_dir)

    second = ingest(root, demo_deck, filename="renamed-copy.pptx")

    assert second.duplicate is True
    assert second.record == first
    assert second.record.source_file == "5G_RAN_Operations_Demo.pptx"
    assert fake_embeddings.document_calls == calls_after_first
    assert durable_state(data_dir) == before
    metadata = root.store.get(include=["metadatas"])["metadatas"]
    assert {m["source_file"] for m in metadata} == {"5G_RAN_Operations_Demo.pptx"}


def test_reopened_root_restores_documents_and_retrieves(
    root, demo_deck: Path, make_settings, fake_embeddings
) -> None:
    record = ingest(root, demo_deck).record
    reopened = open_data_root(make_settings(key=TEST_PLACEHOLDER_KEY), fake_embeddings)
    assert reopened.degraded == []
    assert reopened.list_documents() == [record]
    hits = retrieve_snapshot(reopened, "What was the peak latency during INC-042?")
    assert hits and all(h.chunk.file_sha256 == record.file_sha256 for h in hits)


def test_retrieve_snapshot_empty_index_skips_embedding(root, fake_embeddings) -> None:
    assert retrieve_snapshot(root, "anything") == []
    assert fake_embeddings.query_calls == 0


# ── Coordination lock ───────────────────────────────────────────────────


def test_lock_held_makes_ingest_and_snapshot_busy(root, demo_deck: Path) -> None:
    assert root.lock.acquire(blocking=False)
    try:
        with pytest.raises(BusyError):
            retrieve_snapshot(root, "question")
        with pytest.raises(BusyError), exclusive(root):
            pass
    finally:
        root.lock.release()
    staged = stage_upload(io.BytesIO(demo_deck.read_bytes()), root.settings)
    try:
        with pytest.raises(RuntimeError, match="coordination lock"):
            ingest_staged(root, staged, "deck.pptx")
    finally:
        staged.discard()


def test_retrieval_during_ingest_is_busy_not_partial(make_settings, demo_deck: Path) -> None:
    """Consistency: a snapshot attempted while chunks are being written sees nothing."""
    observed: list[object] = []

    class ProbingEmbeddings(HashEmbeddings):
        def embed_documents(self, texts):
            try:
                observed.append(retrieve_snapshot(opened, "What was the peak latency?"))
            except BusyError as exc:
                observed.append(exc)
            return super().embed_documents(texts)

    opened = open_data_root(make_settings(), ProbingEmbeddings())
    ingest(opened, demo_deck)
    assert len(observed) == 1 and isinstance(observed[0], BusyError)
    assert retrieve_snapshot(opened, "What was the peak latency during INC-042?")


_REPO_ROOT = Path(__file__).resolve().parents[1]

_INGEST_CHILD = """
import sys
from app.config import load_settings
from app.ingestion import exclusive, ingest_staged, open_data_root, stage_upload
from conftest import HashEmbeddings
root = open_data_root(load_settings(), HashEmbeddings())
with open(sys.argv[1], "rb") as handle, exclusive(root):
    staged = stage_upload(handle, root.settings)
    print(ingest_staged(root, staged, "5G_RAN_Operations_Demo.pptx").record.file_sha256)
"""

_QUERY_CHILD = """
import json
from app.config import load_settings
from app.ingestion import open_data_root, retrieve_snapshot
from conftest import HashEmbeddings
root = open_data_root(load_settings(), HashEmbeddings())
hits = retrieve_snapshot(root, "What PRB utilization was observed during congestion?")
print(json.dumps({"degraded": root.degraded, "documents": len(root.documents),
                  "hits": [[h.chunk.file_sha256, h.chunk.slide_number] for h in hits]}))
"""


def _child(script: str, data_dir: Path, *args: str) -> str:
    env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
    env["DATA_DIR"] = str(data_dir)
    env["PYTHONPATH"] = os.pathsep.join([str(_REPO_ROOT), str(_REPO_ROOT / "tests")])
    completed = subprocess.run(
        [sys.executable, "-c", NETWORK_GUARD_SRC + textwrap.dedent(script), *args],
        cwd=_REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return completed.stdout.strip()


def test_fresh_process_reopens_ingested_root(data_dir: Path, demo_deck: Path) -> None:
    """QG-04 through the ingestion path: manifest and chunks survive a new process."""
    sha = _child(_INGEST_CHILD, data_dir, str(demo_deck))
    result = json.loads(_child(_QUERY_CHILD, data_dir))
    assert result["degraded"] == [] and result["documents"] == 1
    assert result["hits"] and all(hit[0] == sha for hit in result["hits"])
    assert 5 in [hit[1] for hit in result["hits"]]


# ── QG-08: invalid, oversized and malformed uploads fail safely ────────


def _zip_bytes(members: list[tuple[str, bytes]]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, data in members:
            archive.writestr(zipfile.ZipInfo(name), data)
    return buffer.getvalue()


_MINIMAL = [("[Content_Types].xml", b"<Types/>"), ("ppt/presentation.xml", b"<p/>")]


def _deck_with(tmp_path: Path, members: list[tuple[str, bytes]], name: str = "x.pptx") -> Path:
    return _write(tmp_path, name, _zip_bytes(members))


def _real_deck_plus(
    tmp_path: Path, deck: Path, extra: list[tuple[str, bytes]], drop: str | None = None
) -> Path:
    """The valid demo deck with hostile members added (or one removed): only the specific
    structural check can reject it, since python-pptx would otherwise parse it."""
    with zipfile.ZipFile(deck) as archive:
        members = [(i.filename, archive.read(i)) for i in archive.infolist() if i.filename != drop]
    return _deck_with(tmp_path, [*members, *extra])


def _member(deck: Path, name: str) -> tuple[str, bytes]:
    with zipfile.ZipFile(deck) as archive:
        return name, archive.read(name)


def _write(tmp_path: Path, name: str, data: bytes) -> Path:
    path = tmp_path / name
    path.write_bytes(data)
    return path


@pytest.mark.filterwarnings("ignore:Duplicate name")
@pytest.mark.parametrize(
    ("builder", "filename", "code"),
    [
        (lambda t, d: d, "deck.ppt", "not_pptx"),
        (lambda t, d: d, "deck.pptx.exe", "not_pptx"),
        (lambda t, d: d, "\x00\x01", "invalid_form"),
        (lambda t, d: _write(t, "fake.pptx", b"not a zip at all"), None, "invalid_pptx"),
        (lambda t, d: _write(t, "cut.pptx", d.read_bytes()[:2000]), None, "invalid_pptx"),
        (lambda t, d: _real_deck_plus(t, d, [], drop="ppt/presentation.xml"), None, "invalid_pptx"),
        (lambda t, d: _real_deck_plus(t, d, [("../evil.txt", b"x")]), None, "invalid_pptx"),
        (lambda t, d: _real_deck_plus(t, d, [("/etc/evil", b"x")]), None, "invalid_pptx"),
        (lambda t, d: _real_deck_plus(t, d, [("C:/evil", b"x")]), None, "invalid_pptx"),
        (lambda t, d: _real_deck_plus(t, d, [("ppt\\..\\evil", b"x")]), None, "invalid_pptx"),
        (
            lambda t, d: _real_deck_plus(t, d, [_member(d, "docProps/app.xml")]),
            None,
            "invalid_pptx",
        ),
        (lambda t, d: _deck_with(t, _MINIMAL), None, "invalid_pptx"),  # not a real package
        (lambda t, d: make_pptx(t / "blank.pptx", [[], []], notes="notes only"), None, "no_text"),
    ],
    ids=[
        "wrong-extension",
        "double-extension",
        "empty-filename",
        "non-zip-bytes",
        "truncated-zip",
        "missing-presentation-xml",
        "dotdot-member",
        "absolute-member",
        "drive-member",
        "backslash-dotdot-member",
        "duplicate-members",
        "malformed-package",
        "no-extractable-text",
    ],
)
def test_ingest_rejects_invalid_uploads_without_state(
    root, demo_deck: Path, tmp_path: Path, data_dir, fake_embeddings, builder, filename, code
) -> None:
    path = builder(tmp_path, demo_deck)
    before = durable_state(data_dir)
    with pytest.raises(UploadRejected) as rejected:
        ingest(root, path, filename=filename)
    assert rejected.value.code == code
    assert durable_state(data_dir) == before
    assert list((data_dir / "tmp").iterdir()) == []
    assert fake_embeddings.document_calls == 0
    assert root.degraded == []


@pytest.mark.parametrize(
    ("constant", "value", "code"),
    [
        ("MAX_UPLOAD_BYTES", 1024, "file_too_large"),
        ("MAX_ZIP_MEMBERS", 5, "archive_limits"),
        ("MAX_UNCOMPRESSED_BYTES", 10_000, "archive_too_large"),
        ("MAX_SLIDES", 3, "archive_limits"),
        ("MAX_EXTRACTED_CHARS", 200, "too_much_text"),
    ],
)
def test_ingest_enforces_size_limits(
    root, demo_deck: Path, data_dir, monkeypatch: pytest.MonkeyPatch, constant, value, code
) -> None:
    monkeypatch.setattr(ingestion, constant, value)
    before = durable_state(data_dir)
    with pytest.raises(UploadRejected) as rejected:
        ingest(root, demo_deck)
    assert rejected.value.code == code
    assert durable_state(data_dir) == before
    assert list((data_dir / "tmp").iterdir()) == []


def test_stage_upload_rejects_empty_file(root, data_dir) -> None:
    with pytest.raises(UploadRejected) as rejected:
        stage_upload(io.BytesIO(b""), root.settings)
    assert rejected.value.code == "empty_file"
    assert list((data_dir / "tmp").iterdir()) == []


# ── Handled failure cleanup, retry and failed cleanup ───────────────────


def test_provider_failure_during_indexing_leaves_nothing_and_retry_succeeds(
    root, demo_deck: Path, data_dir, fake_embeddings
) -> None:
    before = durable_state(data_dir)
    fake_embeddings.fail_next = 1
    with pytest.raises(ProviderError):
        ingest(root, demo_deck)
    assert durable_state(data_dir) == before
    assert root.degraded == [] and root.documents == {}

    outcome = ingest(root, demo_deck)
    assert outcome.duplicate is False
    assert stored_ids(data_dir) == sorted(outcome.record.chunk_ids)


def test_failure_after_chunks_written_is_rolled_back(
    root, demo_deck: Path, data_dir, monkeypatch: pytest.MonkeyPatch
) -> None:
    before = durable_state(data_dir)
    real_write = ingestion.write_manifest

    def failing_write(settings, documents):
        raise OSError("disk full (injected)")

    monkeypatch.setattr(ingestion, "write_manifest", failing_write)
    with pytest.raises(OSError, match="injected"):
        ingest(root, demo_deck)
    assert durable_state(data_dir) == before  # chunks and renamed upload removed
    assert root.degraded == []

    monkeypatch.setattr(ingestion, "write_manifest", real_write)
    assert ingest(root, demo_deck).duplicate is False
    assert len(manifest_documents(data_dir)) == 1


def test_failed_cleanup_degrades_and_preserves_data(
    root, demo_deck: Path, data_dir, monkeypatch: pytest.MonkeyPatch
) -> None:
    def failing_write(settings, documents):
        raise OSError("injected")

    def failing_delete(store, ids):
        raise RuntimeError("injected delete failure")

    monkeypatch.setattr(ingestion, "write_manifest", failing_write)
    monkeypatch.setattr(ingestion, "_delete_chunks", failing_delete)
    with pytest.raises(OSError):
        ingest(root, demo_deck)
    assert root.degraded == ["cleanup_failed"]
    assert stored_ids(data_dir)  # uncertain chunks preserved, not deleted
    assert manifest_documents(data_dir) == []  # never recorded as complete
    with pytest.raises(DegradedError):
        retrieve_snapshot(root, "What was the peak latency during INC-042?")
    with pytest.raises(DegradedError), exclusive(root):
        pass


# ── Startup consistency (data preserved, root degraded) ─────────────────


def test_empty_root_is_initialised(make_settings, fake_embeddings, data_dir) -> None:
    opened = open_data_root(make_settings(), fake_embeddings)
    assert opened.degraded == [] and opened.store is not None
    manifest = json.loads((data_dir / "manifest.json").read_text())
    assert manifest["manifest_version"] == 1 and manifest["documents"] == []
    assert (data_dir / "uploads").is_dir()


def test_abandoned_temporaries_are_removed_at_startup(
    make_settings, fake_embeddings, data_dir
) -> None:
    (data_dir / "tmp").mkdir()
    (data_dir / "tmp" / "abandoned.upload").write_bytes(b"partial")
    (data_dir / ".manifest-abc.tmp").write_text("{")
    opened = open_data_root(make_settings(), fake_embeddings)
    assert opened.degraded == []
    assert list((data_dir / "tmp").iterdir()) == []
    assert not (data_dir / ".manifest-abc.tmp").exists()


def _corrupt(data_dir: Path, record_sha: str, case: str) -> None:
    manifest = data_dir / "manifest.json"
    if case == "manifest_missing":
        manifest.unlink()
    elif case == "manifest_corrupt":
        manifest.write_text("{not json")
    elif case == "manifest_record_corrupt":
        data = json.loads(manifest.read_text())
        data["documents"][0]["slide_number_typo"] = 1
        manifest.write_text(json.dumps(data))
    elif case == "manifest_version_unknown":
        data = json.loads(manifest.read_text())
        data["manifest_version"] = 99
        manifest.write_text(json.dumps(data))
    elif case == "upload_missing":
        (data_dir / "uploads" / f"{record_sha}.pptx").unlink()
    elif case == "unexplained_uploads":
        (data_dir / "uploads" / ("c" * 64 + ".pptx")).write_bytes(b"PK")
    elif case in ("chunks_missing", "unexplained_chunks"):
        client = chromadb.PersistentClient(
            path=str(data_dir / "chroma"), settings=ChromaSettings(anonymized_telemetry=False)
        )
        collection = client.get_collection(COLLECTION_NAME, embedding_function=None)
        if case == "chunks_missing":
            collection.delete(ids=[collection.get(include=[])["ids"][0]])
        else:
            collection.add(ids=["stray"], embeddings=[[0.1] * 1536], documents=["SYNTHETIC"])


@pytest.mark.parametrize(
    ("case", "reason"),
    [
        ("manifest_missing", "manifest_missing"),
        ("manifest_corrupt", "manifest_corrupt"),
        ("manifest_record_corrupt", "manifest_corrupt"),
        ("manifest_version_unknown", "manifest_version_unknown"),
        ("upload_missing", "upload_missing"),
        ("unexplained_uploads", "unexplained_uploads"),
        ("chunks_missing", "chunks_missing"),
        ("unexplained_chunks", "unexplained_chunks"),
    ],
)
def test_inconsistent_root_degrades_and_preserves_data(
    root, demo_deck: Path, data_dir, make_settings, fake_embeddings, case, reason
) -> None:
    record = ingest(root, demo_deck).record
    _corrupt(data_dir, record.file_sha256, case)
    before = durable_state(data_dir)

    reopened = open_data_root(make_settings(key=TEST_PLACEHOLDER_KEY), fake_embeddings)

    assert reason in reopened.degraded
    assert durable_state(data_dir) == before
    with pytest.raises(DegradedError):
        retrieve_snapshot(reopened, "What was the peak latency during INC-042?")


def test_index_config_mismatch_degrades_without_mutation(
    root, demo_deck: Path, data_dir, make_settings, fake_embeddings
) -> None:
    ingest(root, demo_deck)
    before = durable_state(data_dir)
    other = make_settings(key=TEST_PLACEHOLDER_KEY, EMBEDDING_MODEL="text-embedding-3-large")
    reopened = open_data_root(other, fake_embeddings)
    assert reopened.degraded == ["index_config_mismatch"]
    assert durable_state(data_dir) == before


def test_unavailable_root_degrades(make_settings, fake_embeddings, tmp_path: Path) -> None:
    blocker = tmp_path / "not-a-directory"
    blocker.write_text("file in the way")
    settings = make_settings(DATA_DIR=str(blocker))
    opened = open_data_root(settings, fake_embeddings)
    assert opened.degraded == ["data_root_unavailable"]
    assert blocker.read_text() == "file in the way"
