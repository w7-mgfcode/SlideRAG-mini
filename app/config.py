"""Settings, constants, data-root resolution and index configuration.

This is the only module that reads the process environment. Settings are read
once (``load_settings``) and passed to the other modules explicitly. No ``.env``
file is loaded automatically.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

DEFAULT_LLM_MODEL = "gpt-4.1-mini"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_DATA_DIR = "data"
DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"

# External-call bounds (EXEC-01 § 5: finite timeouts/retries).
OPENAI_TIMEOUT_SECONDS = 30.0
OPENAI_MAX_RETRIES = 2
EMBEDDING_BATCH_SIZE = 100

# Index configuration identity (EXEC-01 § 3). Bump a version when its meaning changes.
INDEX_SCHEMA_VERSION = 1
EMBEDDING_DIMENSIONS = 1536
DISTANCE_METRIC = "cosine"
EXTRACTOR_VERSION = "pptx-text-v1"
CHUNKING_VERSION = "slide-split-1000-150-v1"
COLLECTION_NAME = "sliderag_chunks"

RETRIEVAL_K = 5


class ConfigError(ValueError):
    """Raised when the environment holds an unusable setting."""


@dataclass(frozen=True)
class DataPaths:
    """Application-owned storage paths, all contained under the resolved DATA_DIR."""

    root: Path
    uploads: Path
    chroma: Path
    manifest: Path


@dataclass(frozen=True)
class IndexConfig:
    """Non-secret identity of the vector space. Never contains credentials."""

    schema_version: int
    embedding_model: str
    embedding_endpoint: str
    embedding_dimensions: int
    distance: str
    extractor_version: str
    chunking_version: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)

    def fingerprint(self) -> str:
        canonical = json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None = field(repr=False)
    llm_model: str
    embedding_model: str
    llm_base_url: str | None
    embedding_base_url: str | None
    data_dir: Path

    @property
    def openai_api_key_set(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def paths(self) -> DataPaths:
        return data_paths(self.data_dir)

    @property
    def index_config(self) -> IndexConfig:
        return IndexConfig(
            schema_version=INDEX_SCHEMA_VERSION,
            embedding_model=self.embedding_model,
            embedding_endpoint=endpoint_identity(self.embedding_base_url),
            embedding_dimensions=EMBEDDING_DIMENSIONS,
            distance=DISTANCE_METRIC,
            extractor_version=EXTRACTOR_VERSION,
            chunking_version=CHUNKING_VERSION,
        )


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _validate_base_url(name: str, value: str | None) -> str | None:
    if value is None:
        return None
    parts = urlsplit(value)
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        raise ConfigError(f"{name} must be an http(s) URL with a host")
    if parts.username is not None or parts.password is not None:
        raise ConfigError(f"{name} must not embed credentials")
    if parts.query or parts.fragment:
        raise ConfigError(f"{name} must not contain a query string or fragment")
    return value.rstrip("/")


def endpoint_identity(base_url: str | None) -> str:
    """Non-secret endpoint identity recorded in the index configuration."""
    parts = urlsplit(base_url or DEFAULT_OPENAI_BASE_URL)
    # Scheme/host are case-insensitive; a path may identify a different backend
    # when its case changes. Config validation already excludes URL credentials.
    return parts._replace(
        scheme=parts.scheme.lower(), netloc=parts.netloc.lower(), path=parts.path.rstrip("/")
    ).geturl()


def resolve_data_dir(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if root == Path(root.anchor):
        raise ConfigError("DATA_DIR must not be a filesystem root")
    return root


def contained(root: Path, *parts: str) -> Path:
    """Return ``root/parts`` resolved, rejecting any path that escapes ``root``."""
    candidate = root.joinpath(*parts).resolve()
    if not candidate.is_relative_to(root):
        raise ConfigError("path escapes DATA_DIR")
    return candidate


def data_paths(root: Path) -> DataPaths:
    return DataPaths(
        root=root,
        uploads=contained(root, "uploads"),
        chroma=contained(root, "chroma"),
        manifest=contained(root, "manifest.json"),
    )


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    """Read settings once from the process environment (or an explicit mapping)."""
    env = os.environ if environ is None else environ
    return Settings(
        openai_api_key=_clean(env.get("OPENAI_API_KEY")),
        llm_model=_clean(env.get("LLM_MODEL")) or DEFAULT_LLM_MODEL,
        embedding_model=_clean(env.get("EMBEDDING_MODEL")) or DEFAULT_EMBEDDING_MODEL,
        llm_base_url=_validate_base_url("LLM_BASE_URL", _clean(env.get("LLM_BASE_URL"))),
        embedding_base_url=_validate_base_url(
            "EMBEDDING_BASE_URL", _clean(env.get("EMBEDDING_BASE_URL"))
        ),
        data_dir=resolve_data_dir(_clean(env.get("DATA_DIR")) or DEFAULT_DATA_DIR),
    )
