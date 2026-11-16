"""Shared fixtures: deterministic fakes, the generated demo deck, temp data roots.

Offline tests here are mocked evidence only. They do not prove real embedding,
real native structured output, or real-model behavior. Fakes live only here.
"""

from __future__ import annotations

import hashlib
import math
import os
import re
import socket
from collections.abc import Sequence
from pathlib import Path

import httpx
import openai
import pytest
from langchain_core.embeddings import Embeddings
from langchain_core.messages import AIMessage

from app.config import EMBEDDING_DIMENSIONS, Settings, load_settings
from app.rag import StructuredAnswer
from demo.generate_pptx import write_deck

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


TRACING_FLAGS = ("LANGSMITH_TRACING", "LANGSMITH_TRACING_V2", "LANGCHAIN_TRACING_V2")
# Legacy V1 flag: langchain-core refuses "true" outright, so it is removed, not set.
_LEGACY_TRACING_FLAG = "LANGCHAIN_TRACING"
_TRACING_ENDPOINTS = ("LANGSMITH_ENDPOINT", "LANGCHAIN_ENDPOINT")
_TRACING_KEYS = ("LANGSMITH_API_KEY", "LANGCHAIN_API_KEY")


@pytest.fixture(autouse=True)
def no_ambient_tracing(monkeypatch: pytest.MonkeyPatch):
    """Suite-wide guard (offline and live): tests never send text to LangSmith.

    An ambient developer shell may enable tracing. Force it off, drop any tracing key
    and point the endpoints at the loopback discard port, so even a regression fails
    locally instead of uploading test text. langsmith caches env lookups.
    """
    from langsmith.utils import get_env_var

    for name in TRACING_FLAGS:
        monkeypatch.setenv(name, "false")
    for name in _TRACING_ENDPOINTS:
        monkeypatch.setenv(name, "http://127.0.0.1:9")
    for name in (*_TRACING_KEYS, _LEGACY_TRACING_FLAG):
        monkeypatch.delenv(name, raising=False)
    get_env_var.cache_clear()
    yield
    get_env_var.cache_clear()


class HashEmbeddings(Embeddings):
    """Deterministic bag-of-words embedding (offline fake; not semantic).

    Counts calls so tests can assert "zero embedding calls" (QG-03). Setting
    ``fail_next`` makes the next N calls raise a provider timeout.
    """

    def __init__(self, size: int = EMBEDDING_DIMENSIONS) -> None:
        self.size = size
        self.document_calls = 0
        self.query_calls = 0
        self.fail_next = 0

    def _maybe_fail(self) -> None:
        if self.fail_next > 0:
            self.fail_next -= 1
            raise openai.APITimeoutError(
                request=httpx.Request("POST", "https://provider.invalid/v1/embeddings")
            )

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.size
        for token in re.findall(r"[a-z0-9-]+", text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            vector[int.from_bytes(digest[:4], "big") % self.size] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        self.document_calls += 1
        self._maybe_fail()
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        self.query_calls += 1
        self._maybe_fail()
        return self._embed(text)


_LABEL_LINE = re.compile(r"^\[(S\d+)\] file: (.*) \| slide: (\d+)$", re.MULTILINE)


class FakeGenerator:
    """Deterministic structured generator returning a configurable ``StructuredAnswer``.

    By default it answers and cites ``S1``. It records the label lines it was shown
    (``seen``: label → (file, slide)) so tests can map citations back to slides.
    """

    def __init__(
        self,
        answer: str = "Synthetic answer from the cited slide.",
        cited: Sequence[str] = ("S1",),
        insufficient: bool = False,
    ) -> None:
        self.answer = answer
        self.cited = list(cited)
        self.insufficient = insufficient
        self.error: Exception | None = None
        self.calls = 0
        self.seen: dict[str, tuple[str, int]] = {}

    def __call__(self, messages):
        self.calls += 1
        if self.error is not None:
            raise self.error
        self.seen = {
            label: (name, int(slide))
            for label, name, slide in _LABEL_LINE.findall(messages[-1].content)
        }
        parsed = StructuredAnswer(
            answer=self.answer, cited=list(self.cited), insufficient=self.insufficient
        )
        return {"raw": AIMessage(content=""), "parsed": parsed, "parsing_error": None}


def make_pptx(path: Path, slides: Sequence[Sequence[str]], notes: str | None = None) -> Path:
    """Small synthetic deck: one text box per string on each slide (empty list = blank)."""
    from pptx import Presentation
    from pptx.util import Inches

    prs = Presentation()
    for texts in slides:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        for i, text in enumerate(texts):
            box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5 + i), Inches(8), Inches(0.8))
            box.text_frame.text = text
        if notes:
            slide.notes_slide.notes_text_frame.text = notes
    prs.save(str(path))
    return path


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


@pytest.fixture
def fake_generator() -> FakeGenerator:
    return FakeGenerator()


@pytest.fixture(scope="session")
def demo_deck(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """The ten-slide demo deck, generated by demo/generate_pptx.py (never committed)."""
    return write_deck(tmp_path_factory.mktemp("deck") / "5G_RAN_Operations_Demo.pptx")
