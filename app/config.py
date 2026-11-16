"""Settings, constants, data-root resolution and index configuration.

This is the only module that reads the process environment. Settings are read
once (``load_settings``) and passed to the other modules explicitly. No ``.env``
file is loaded automatically.

Endpoints: ``LLM_BASE_URL`` and ``EMBEDDING_BASE_URL`` must be credential-free
``https`` URLs with a syntactically valid ASCII host (IDNs in punycode form) and
port, and no query or fragment. Unset endpoints resolve to the explicit
``DEFAULT_OPENAI_BASE_URL``; ambient SDK base-URL variables (``OPENAI_BASE_URL``,
``OPENAI_API_BASE``, ``LANGSMITH_GATEWAY``) are ignored. ``Settings`` validates and
canonicalises endpoints on every construction (including ``dataclasses.replace``),
so the URL sent to the clients is the same string recorded in the index identity.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import re
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
# 2: endpoints are explicit and canonical. Version-1 indexes may have been embedded
# through an ambient SDK endpoint while recording the default, so they are refused.
INDEX_SCHEMA_VERSION = 2
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
    # Optional endpoints; None means DEFAULT_OPENAI_BASE_URL (never SDK env vars).
    # Stored in canonical form after validation in __post_init__.
    llm_base_url: str | None
    embedding_base_url: str | None
    data_dir: Path

    def __post_init__(self) -> None:
        # Runs for load_settings, direct construction and dataclasses.replace alike,
        # so no Settings instance can carry an unvalidated endpoint.
        for attr, name in (
            ("llm_base_url", "LLM_BASE_URL"),
            ("embedding_base_url", "EMBEDDING_BASE_URL"),
        ):
            object.__setattr__(self, attr, canonical_base_url(name, getattr(self, attr)))

    @property
    def openai_api_key_set(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def effective_llm_base_url(self) -> str:
        """Chat endpoint every client uses: the configured value or the explicit default."""
        return self.llm_base_url or DEFAULT_OPENAI_BASE_URL

    @property
    def effective_embedding_base_url(self) -> str:
        """Embedding endpoint used for requests and recorded in the index identity."""
        return self.embedding_base_url or DEFAULT_OPENAI_BASE_URL

    @property
    def paths(self) -> DataPaths:
        return data_paths(self.data_dir)

    @property
    def index_config(self) -> IndexConfig:
        return IndexConfig(
            schema_version=INDEX_SCHEMA_VERSION,
            embedding_model=self.embedding_model,
            embedding_endpoint=self.effective_embedding_base_url,
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


_HOST_LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?")


def _valid_hostname(host: str) -> bool:
    """ASCII DNS name (RFC 1123 labels) or an IP literal. Non-ASCII hosts are refused."""
    if host.startswith("[") and host.endswith("]"):
        try:
            return ipaddress.ip_address(host[1:-1]).version == 6
        except ValueError:
            return False
    if not host.isascii() or len(host) > 253:
        return False
    return all(_HOST_LABEL.fullmatch(label) for label in host.split("."))


def canonical_base_url(name: str, value: str | None) -> str | None:
    """Validate an endpoint and return its one canonical form (or None when unset).

    Accepts only a credential-free ``https`` URL with a valid host and port and no
    query or fragment. Canonical form: lowercase scheme and host, path case kept,
    trailing slash stripped, explicit default port 443 dropped. Errors never echo
    the value.
    """
    if value is None:
        return None
    if not isinstance(value, str) or any(c.isspace() or not c.isprintable() for c in value):
        raise ConfigError(f"{name} is not a valid URL")
    try:
        parts = urlsplit(value)
        port = parts.port  # raises ValueError for a non-numeric or out-of-range port
    except ValueError:
        raise ConfigError(f"{name} is not a valid URL") from None
    if parts.scheme.lower() != "https" or not parts.hostname:
        raise ConfigError(f"{name} must be an https URL with a host")
    if port == 0:
        raise ConfigError(f"{name} has an invalid port")
    if parts.username is not None or parts.password is not None or "@" in parts.netloc:
        raise ConfigError(f"{name} must not embed credentials")
    if parts.query or parts.fragment or "?" in value or "#" in value:
        raise ConfigError(f"{name} must not contain a query string or fragment")
    host_port = parts.netloc.lower()
    host = host_port.rsplit(":", 1)[0] if ":" in host_port.rsplit("]", 1)[-1] else host_port
    if not _valid_hostname(host):
        raise ConfigError(f"{name} has an invalid host")
    netloc = host if port in (None, 443) else f"{host}:{port}"
    return f"https://{netloc}{parts.path.rstrip('/')}"


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
        # Validated and canonicalised in Settings.__post_init__.
        llm_base_url=_clean(env.get("LLM_BASE_URL")),
        embedding_base_url=_clean(env.get("EMBEDDING_BASE_URL")),
        data_dir=resolve_data_dir(_clean(env.get("DATA_DIR")) or DEFAULT_DATA_DIR),
    )
