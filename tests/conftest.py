"""Shared fixtures: deterministic fake embeddings, temp data roots, network guard.

Offline tests here are mocked evidence only. They do not prove real embedding,
real native structured output, or real-model behavior.
"""

from __future__ import annotations

import hashlib
import math
import os
import re
import socket
from pathlib import Path

import pytest
from langchain_core.embeddings import Embeddings

from app.config import EMBEDDING_DIMENSIONS, Settings, load_settings

TEST_PLACEHOLDER_KEY = "test-placeholder"

# Prepended to subprocess scripts so child processes are network-guarded too.
NETWORK_GUARD_SRC = """
import socket as _socket
def _blocked(self, address, *a, **k):
    if self.family in (_socket.AF_INET, _socket.AF_INET6):
        raise RuntimeError(f"network access blocked in offline test: {address!r}")
    return _orig_connect(self, address, *a, **k)
_orig_connect = _socket.socket.connect
_socket.socket.connect = _blocked
_socket.socket.connect_ex = _blocked
"""


class HashEmbeddings(Embeddings):
    """Deterministic bag-of-words embedding (offline fake; not semantic)."""

    def __init__(self, size: int = EMBEDDING_DIMENSIONS) -> None:
        self.size = size

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.size
        for token in re.findall(r"[a-z0-9-]+", text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            vector[int.from_bytes(digest[:4], "big") % self.size] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


RUN_LIVE_OPTION = "--run-live"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        RUN_LIVE_OPTION,
        action="store_true",
        default=False,
        help=(
            "Run @pytest.mark.integration live provider checks. Also requires a nonblank "
            "OPENAI_API_KEY; otherwise they are skipped. "
            "Usage: uv run pytest -m integration --run-live"
        ),
    )


def live_skip_reason(run_live: bool, api_key: str | None) -> str | None:
    """Why integration tests are skipped, or None when the live opt-in is complete."""
    if not run_live:
        return f"integration: live checks need explicit {RUN_LIVE_OPTION} (deferred)"
    if not (api_key or "").strip():
        return "integration: OPENAI_API_KEY not set or blank (live check deferred)"
    return None


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    # Presence check only; the key value is never written to test output.
    reason = live_skip_reason(
        bool(config.getoption(RUN_LIVE_OPTION)), os.environ.get("OPENAI_API_KEY")
    )
    if reason is None:
        return
    skip = pytest.mark.skip(reason=reason)
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)


@pytest.fixture(autouse=True)
def block_network(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail any Python-level TCP connection in offline tests."""
    if "integration" in request.keywords:
        return
    original = socket.socket.connect

    def guarded(self: socket.socket, address: object, *args: object, **kwargs: object) -> object:
        if self.family in (socket.AF_INET, socket.AF_INET6):
            raise RuntimeError(f"network access blocked in offline test: {address!r}")
        return original(self, address, *args, **kwargs)

    monkeypatch.setattr(socket.socket, "connect", guarded)
    monkeypatch.setattr(socket.socket, "connect_ex", guarded)


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    root = tmp_path / "data"
    root.mkdir()
    return root


@pytest.fixture
def make_settings(data_dir: Path):
    def factory(key: str | None = None, **overrides: str) -> Settings:
        env = {"DATA_DIR": str(data_dir), **overrides}
        if key is not None:
            env["OPENAI_API_KEY"] = key
        return load_settings(env)

    return factory


@pytest.fixture
def fake_embeddings() -> HashEmbeddings:
    return HashEmbeddings()
