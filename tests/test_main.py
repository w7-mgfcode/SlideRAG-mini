"""Route and settings tests (offline; injected settings and fakes, no network).

Mocked evidence only: the browser check ``local-upload-answer`` needs a live
provider and is deferred, not simulated here.
"""

from __future__ import annotations

import dataclasses
import html
import json
import re
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

import app.main
from app.config import MAX_QUESTION_CHARS, ConfigError, Settings, contained, load_settings
from app.main import create_app
from app.rag import FALLBACK_MESSAGE, ProviderError
from conftest import TEST_PLACEHOLDER_KEY, FakeGenerator, make_pptx

PPTX_TYPE = "application/vnd.openxmlformats-officedocument.presentationml.presentation"


def test_health_without_key_returns_degraded_503(make_settings, data_dir: Path) -> None:
    with TestClient(create_app(make_settings())) as client:
        response = client.get("/health")
    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "reasons": ["openai_api_key_missing"],
        "openai_api_key_set": False,
    }
    assert str(data_dir) not in response.text


def test_health_with_configured_key_returns_ok(make_settings, data_dir: Path) -> None:
    with TestClient(create_app(make_settings(key=TEST_PLACEHOLDER_KEY))) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "openai_api_key_set": True}
    assert TEST_PLACEHOLDER_KEY not in response.text
    assert str(data_dir) not in response.text


def test_load_settings_repr_hides_key_and_derives_paths(data_dir: Path) -> None:
    settings = load_settings({"OPENAI_API_KEY": TEST_PLACEHOLDER_KEY, "DATA_DIR": str(data_dir)})
    assert settings.openai_api_key_set is True
    assert TEST_PLACEHOLDER_KEY not in repr(settings)
    assert TEST_PLACEHOLDER_KEY not in str(settings.index_config.as_dict())
    paths = settings.paths
    assert (paths.uploads, paths.chroma, paths.manifest) == (
        data_dir / "uploads",
        data_dir / "chroma",
        data_dir / "manifest.json",
    )
    assert settings.index_config.distance == "cosine"
    assert settings.index_config.embedding_endpoint == "https://api.openai.com/v1"


def test_load_settings_blank_key_is_unset(data_dir: Path) -> None:
    settings = load_settings({"OPENAI_API_KEY": "   ", "DATA_DIR": str(data_dir)})
    assert settings.openai_api_key is None
    assert settings.openai_api_key_set is False


def test_index_identity_preserves_endpoint_path_case(data_dir: Path) -> None:
    def identity(endpoint: str) -> str:
        return load_settings(
            {"DATA_DIR": str(data_dir), "EMBEDDING_BASE_URL": endpoint}
        ).index_config.fingerprint()

    assert identity("https://example.invalid/TeamA/v1") != identity(
        "https://example.invalid/teama/v1"
    )
    assert identity("HTTPS://EXAMPLE.INVALID/TeamA/v1/") == identity(
        "https://example.invalid/TeamA/v1"
    )


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("EMBEDDING_BASE_URL", "https://user:secret@example.invalid/v1"),
        ("LLM_BASE_URL", "ftp://example.invalid/v1"),
        ("LLM_BASE_URL", "https://example.invalid/v1?token=x"),
        ("LLM_BASE_URL", "https://example.invalid/v1#frag"),
        # Comment 1: plaintext http would send the API key without TLS.
        ("LLM_BASE_URL", "http://example.invalid/v1"),
        ("EMBEDDING_BASE_URL", "HTTP://example.invalid/v1"),
        # Comment 11: malformed URLs fail as ConfigError at load time.
        ("EMBEDDING_BASE_URL", "https:///v1"),
        ("EMBEDDING_BASE_URL", "example.invalid/v1"),
        ("LLM_BASE_URL", "https://example.invalid:abc/v1"),
        ("LLM_BASE_URL", "https://example.invalid:65536/v1"),
        ("EMBEDDING_BASE_URL", "https://example.invalid:0/v1"),
        ("EMBEDDING_BASE_URL", "https://[::1/v1"),
        # PR #20 review: hostname syntax and non-ASCII hosts fail as ConfigError.
        # T18 N1: all-numeric hosts must be valid IPv4 (httpx refuses them later otherwise).
        ("LLM_BASE_URL", "https://999.999.1.1/v1"),
        ("EMBEDDING_BASE_URL", "https://1.2.3/v1"),
        ("EMBEDDING_BASE_URL", "https://01.2.3.4/v1"),
        ("LLM_BASE_URL", "https://bad host.invalid/v1"),
        ("LLM_BASE_URL", "https://bad_host.invalid/v1"),
        ("EMBEDDING_BASE_URL", "https://a..b.invalid/v1"),
        ("EMBEDDING_BASE_URL", "https://-a.invalid/v1"),
        ("EMBEDDING_BASE_URL", "https://ex\u00e4mple.invalid/v1"),
        ("DATA_DIR", "/"),
    ],
)
def test_load_settings_rejects_unsafe_values(name: str, value: str, data_dir: Path) -> None:
    with pytest.raises(ConfigError) as error:
        load_settings({"DATA_DIR": str(data_dir), name: value})
    assert value not in str(error.value)  # T18 N2: messages never echo the value
    host = value.split("//", 1)[-1].split("/", 1)[0]
    if host and name != "DATA_DIR":
        assert host not in str(error.value)


def test_load_settings_accepts_valid_ipv4_host(data_dir: Path) -> None:
    settings = load_settings({"DATA_DIR": str(data_dir), "LLM_BASE_URL": "https://10.0.0.7/v1"})
    assert settings.effective_llm_base_url == "https://10.0.0.7/v1"


def test_load_settings_resolves_explicit_effective_endpoints(data_dir: Path) -> None:
    defaults = load_settings({"DATA_DIR": str(data_dir)})
    assert defaults.effective_llm_base_url == "https://api.openai.com/v1"
    assert defaults.effective_embedding_base_url == "https://api.openai.com/v1"

    custom = load_settings(
        {
            "DATA_DIR": str(data_dir),
            "LLM_BASE_URL": "https://chat.example.invalid:8443/v1/",
            "EMBEDDING_BASE_URL": "https://embed.example.invalid/v1",
        }
    )
    assert custom.effective_llm_base_url == "https://chat.example.invalid:8443/v1"
    assert custom.effective_embedding_base_url == "https://embed.example.invalid/v1"
    assert custom.index_config.embedding_endpoint == custom.effective_embedding_base_url


def test_equivalent_endpoints_share_one_canonical_identity(data_dir: Path) -> None:
    """Mixed-case host, trailing slash and explicit :443 agree; path case still differs."""

    def settings(endpoint: str) -> Settings:
        return load_settings({"DATA_DIR": str(data_dir), "EMBEDDING_BASE_URL": endpoint})

    plain = settings("https://embed.example.invalid/TeamA/v1")
    for variant in (
        "https://EMBED.Example.INVALID/TeamA/v1",
        "https://embed.example.invalid/TeamA/v1/",
        "https://embed.example.invalid:443/TeamA/v1",
        "HTTPS://Embed.Example.Invalid:443/TeamA/v1/",
    ):
        other = settings(variant)
        assert other.effective_embedding_base_url == plain.effective_embedding_base_url
        assert other.index_config.fingerprint() == plain.index_config.fingerprint()
    assert plain.effective_embedding_base_url == "https://embed.example.invalid/TeamA/v1"
    assert (
        settings("https://embed.example.invalid/teama/v1").index_config.fingerprint()
        != plain.index_config.fingerprint()
    )
    assert settings("https://embed.example.invalid:8443/TeamA/v1").effective_embedding_base_url == (
        "https://embed.example.invalid:8443/TeamA/v1"
    )


def _direct_settings(data_dir: Path, **endpoints: str | None) -> Settings:
    values: dict[str, str | None] = {"llm_base_url": None, "embedding_base_url": None}
    values.update(endpoints)
    return Settings(
        openai_api_key=TEST_PLACEHOLDER_KEY,
        llm_model="gpt-4.1-mini",
        embedding_model="text-embedding-3-small",
        data_dir=data_dir,
        **values,
    )


@pytest.mark.parametrize("field_name", ["llm_base_url", "embedding_base_url"])
@pytest.mark.parametrize(
    "value",
    [
        "http://example.invalid/v1",
        "https://bad host.invalid/v1",
        "https://bad_host.invalid/v1",
        "https://example.invalid:99999/v1",
        "https://example.invalid:0/v1",
        "https://user:secret@example.invalid/v1",
    ],
)
def test_settings_direct_construction_and_replace_validate_endpoints(
    data_dir: Path, field_name: str, value: str
) -> None:
    """Validation is not limited to load_settings: __init__ and replace() enforce it."""
    with pytest.raises(ConfigError) as direct:
        _direct_settings(data_dir, **{field_name: value})
    valid = _direct_settings(data_dir)
    with pytest.raises(ConfigError) as replaced:
        dataclasses.replace(valid, **{field_name: value})
    for error in (direct, replaced):
        assert "secret" not in str(error.value) and "example.invalid" not in str(error.value)


def test_settings_direct_construction_canonicalises_endpoints(data_dir: Path) -> None:
    direct = _direct_settings(data_dir, llm_base_url="https://Chat.Example.Invalid:443/V1/")
    assert direct.llm_base_url == direct.effective_llm_base_url == "https://chat.example.invalid/V1"
    replaced = dataclasses.replace(direct, embedding_base_url="https://E.Invalid/v1/")
    assert replaced.index_config.embedding_endpoint == "https://e.invalid/v1"


def test_contained_rejects_escape(data_dir: Path) -> None:
    with pytest.raises(ConfigError):
        contained(data_dir, "..", "outside")


# ── Upload → list → answer routes (injected fakes; mocked evidence) ─────


@pytest.fixture
def client_factory(make_settings, fake_embeddings, fake_generator):
    clients: list[TestClient] = []

    def factory(key: str | None = TEST_PLACEHOLDER_KEY, **kwargs) -> TestClient:
        kwargs.setdefault("embeddings", fake_embeddings)
        kwargs.setdefault("generator", fake_generator)
        client = TestClient(create_app(make_settings(key=key), **kwargs))
        client.__enter__()
        clients.append(client)
        return client

    yield factory
    for client in clients:
        client.__exit__(None, None, None)


def _upload(client: TestClient, path: Path, filename: str | None = None) -> httpx.Response:
    with path.open("rb") as handle:
        return client.post("/upload", files={"file": (filename or path.name, handle, PPTX_TYPE)})


def _text(response: httpx.Response) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", response.text))


def test_index_page_renders_empty_state(client_factory) -> None:
    response = client_factory().get("/")
    assert response.status_code == 200
    assert "No documents indexed yet." in response.text
    assert 'enctype="multipart/form-data"' in response.text
    assert "<script" not in response.text  # no JS frontend


def test_upload_list_and_ask_happy_path(
    client_factory, demo_deck: Path, fake_generator: FakeGenerator, data_dir: Path
) -> None:
    client = client_factory()
    uploaded = _upload(client, demo_deck)
    assert uploaded.status_code == 200
    assert "Indexed 5G_RAN_Operations_Demo.pptx: 10 of 10 slides" in _text(uploaded)

    listing = client.get("/")
    assert "5G_RAN_Operations_Demo.pptx" in listing.text

    fake_generator.answer = "Peak latency reached 46 ms [S1]."
    answered = client.post("/ask", data={"question": "What was the peak latency during INC-042?"})
    assert answered.status_code == 200
    file_name, slide = fake_generator.seen["S1"]
    body = _text(answered)
    assert "Peak latency reached 46 ms." in body and "[S1]" not in body
    assert f"{file_name} — slide {slide}" in body
    assert FALLBACK_MESSAGE not in body
    assert str(data_dir) not in answered.text


def test_duplicate_upload_route_adds_nothing(
    client_factory, demo_deck: Path, fake_embeddings
) -> None:
    client = client_factory()
    assert _upload(client, demo_deck).status_code == 200
    calls = fake_embeddings.document_calls
    again = _upload(client, demo_deck, filename="other-name.pptx")
    assert again.status_code == 200
    assert "Already indexed as 5G_RAN_Operations_Demo.pptx" in _text(again)
    assert fake_embeddings.document_calls == calls
    assert "other-name.pptx" not in client.get("/").text


def test_ask_with_empty_index_returns_fallback(client_factory, fake_generator) -> None:
    response = client_factory().post("/ask", data={"question": "Anything indexed?"})
    assert response.status_code == 200
    assert FALLBACK_MESSAGE in _text(response) and "empty_retrieval" in response.text
    assert fake_generator.calls == 0


def test_document_and_model_html_is_escaped(
    client_factory, tmp_path: Path, fake_generator: FakeGenerator
) -> None:
    deck = make_pptx(
        tmp_path / "x.pptx",
        [["SYNTHETIC <script>alert('slide')</script> latency 46 ms"]],
    )
    client = client_factory()
    uploaded = _upload(client, deck, filename="<b>evil<b>.pptx")
    assert uploaded.status_code == 200
    fake_generator.answer = "<img src=x onerror=alert(1)> 46 ms"
    answered = client.post("/ask", data={"question": "<i>latency</i>?"})
    for response in (uploaded, answered, client.get("/")):
        assert "<b>evil" not in response.text and "<img" not in response.text
        assert "<script>" not in response.text and "<i>latency" not in response.text
    assert "&lt;b&gt;evil&lt;b&gt;.pptx" in client.get("/").text
    assert "&lt;img src=x onerror=alert(1)&gt;" in answered.text


@pytest.mark.parametrize(
    ("files", "data", "status"),
    [
        ({"file": ("deck.txt", b"hello", "text/plain")}, None, 415),
        ({"file": ("deck.pptx", b"not a zip", PPTX_TYPE)}, None, 400),
        ({"upload": ("deck.pptx", b"PK", PPTX_TYPE)}, None, 400),
        ({"file": ("deck.pptx", b"", PPTX_TYPE)}, None, 400),
        ({"file": ("deck.pptx", b"PK", PPTX_TYPE)}, {"extra": "field"}, 400),
        (
            [("file", ("a.pptx", b"PK", PPTX_TYPE)), ("file", ("b.pptx", b"PK", PPTX_TYPE))],
            None,
            400,
        ),
    ],
    ids=["wrong-extension", "not-zip", "wrong-field", "empty", "extra-field", "two-files"],
)
def test_upload_rejects_bad_forms_generically(
    client_factory, data_dir, files, data, status
) -> None:
    response = client_factory().post("/upload", files=files, data=data)
    assert response.status_code == status
    assert "hello" not in response.text and "not a zip" not in response.text
    assert "No documents indexed yet." in response.text
    assert list((data_dir / "tmp").iterdir()) == []


def test_upload_requires_multipart(client_factory) -> None:
    response = client_factory().post("/upload", data={"file": "x"})
    assert response.status_code == 415


def test_upload_request_cap_enforced_before_parsing(
    client_factory, demo_deck: Path, data_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(app.main, "MAX_REQUEST_BYTES", 4096)
    client = client_factory()
    declared = _upload(client, demo_deck)
    assert declared.status_code == 413

    # No Content-Length (chunked): the receive-side cap still stops the body.
    boundary = "sliderag-boundary"
    head = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="d.pptx"\r\n'
        f"Content-Type: {PPTX_TYPE}\r\n\r\n"
    ).encode()
    body = head + demo_deck.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    streamed = client.post(
        "/upload",
        content=(body[i : i + 1024] for i in range(0, len(body), 1024)),
        headers={"content-type": f"multipart/form-data; boundary={boundary}"},
    )
    assert streamed.status_code == 413
    assert list((data_dir / "tmp").iterdir()) == []
    assert json.loads((data_dir / "manifest.json").read_text())["documents"] == []


@pytest.mark.parametrize(
    ("data", "status"),
    [
        ({"question": "   "}, 400),
        ({"question": "x" * (MAX_QUESTION_CHARS + 1)}, 400),
        ({"question": "ok", "extra": "1"}, 400),
        ({"other": "ok"}, 400),
        ({"question": "x" * 20_000}, 413),
    ],
    ids=["blank", "too-long", "extra-field", "wrong-field", "over-request-cap"],
)
def test_ask_bounds_the_question(client_factory, fake_generator, data, status) -> None:
    response = client_factory().post("/ask", data=data)
    assert response.status_code == status
    assert "x" * 50 not in response.text
    assert fake_generator.calls == 0


def test_ask_accepts_question_at_limit(client_factory) -> None:
    response = client_factory().post(
        "/ask", data={"question": " " + "x" * MAX_QUESTION_CHARS + " "}
    )
    assert response.status_code == 200


def test_busy_lock_returns_409(client_factory, demo_deck: Path) -> None:
    client = client_factory()
    lock = client.app.state.root.lock
    assert lock.acquire(blocking=False)
    try:
        assert _upload(client, demo_deck).status_code == 409
        assert client.post("/ask", data={"question": "q"}).status_code == 409
    finally:
        lock.release()
    assert _upload(client, demo_deck).status_code == 200


def test_provider_errors_return_502(
    client_factory, demo_deck: Path, fake_embeddings, fake_generator
) -> None:
    client = client_factory()
    fake_embeddings.fail_next = 1
    failed_upload = _upload(client, demo_deck)
    assert failed_upload.status_code == 502
    assert "APITimeoutError" not in failed_upload.text
    assert _upload(client, demo_deck).status_code == 200  # safe retry

    fake_embeddings.fail_next = 1
    assert client.post("/ask", data={"question": "INC-042 latency?"}).status_code == 502
    fake_generator.error = ProviderError("APIConnectionError")
    assert client.post("/ask", data={"question": "INC-042 latency?"}).status_code == 502
    assert client.get("/health").status_code == 200  # provider errors do not degrade


def test_missing_key_blocks_upload_and_ask_with_503(client_factory, demo_deck: Path) -> None:
    client = client_factory(key=None)
    assert client.get("/health").status_code == 503
    assert _upload(client, demo_deck).status_code == 503
    assert client.post("/ask", data={"question": "q"}).status_code == 503


def test_inconsistent_root_degrades_routes_without_leaking_paths(
    client_factory, demo_deck: Path, data_dir: Path
) -> None:
    first = client_factory()
    assert _upload(first, demo_deck).status_code == 200
    (data_dir / "manifest.json").write_text("{corrupt")

    client = client_factory()
    health = client.get("/health")
    assert health.status_code == 503
    assert health.json()["reasons"] == ["manifest_corrupt"]
    for response in (
        health,
        _upload(client, demo_deck),
        client.post("/ask", data={"question": "q"}),
    ):
        assert response.status_code == 503
        assert str(data_dir) not in response.text
    assert (data_dir / "manifest.json").read_text() == "{corrupt"  # preserved


def test_runtime_cleanup_failure_degrades_health(
    client_factory, demo_deck: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import app.ingestion

    def failing_write(settings, documents):
        raise OSError("injected")

    def failing_delete(store, ids):
        raise RuntimeError("injected")

    client = client_factory()
    monkeypatch.setattr(app.ingestion, "write_manifest", failing_write)
    monkeypatch.setattr(app.ingestion, "_delete_chunks", failing_delete)
    failed = _upload(client, demo_deck)
    assert failed.status_code == 503 and "injected" not in failed.text
    health = client.get("/health")
    assert health.status_code == 503 and health.json()["reasons"] == ["cleanup_failed"]
    assert client.post("/ask", data={"question": "q"}).status_code == 503


def test_provider_error_with_failed_cleanup_returns_503(
    client_factory, demo_deck: Path, fake_embeddings, monkeypatch: pytest.MonkeyPatch
) -> None:
    """T23 #4: a degrading rollback outranks the provider 502."""
    import app.ingestion

    def failing_delete(store, ids):
        raise RuntimeError("injected")

    client = client_factory()
    monkeypatch.setattr(app.ingestion, "_delete_chunks", failing_delete)
    fake_embeddings.fail_next = 1
    failed = _upload(client, demo_deck)
    assert failed.status_code == 503 and "injected" not in failed.text
    health = client.get("/health")
    assert health.status_code == 503 and health.json()["reasons"] == ["cleanup_failed"]


def test_rolled_back_storage_failure_returns_500_and_allows_retry(
    client_factory, demo_deck: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import app.ingestion

    real_write = app.ingestion.write_manifest

    def failing_write(settings, documents):
        raise OSError("injected")

    client = client_factory()
    monkeypatch.setattr(app.ingestion, "write_manifest", failing_write)
    failed = _upload(client, demo_deck)
    assert failed.status_code == 500 and "injected" not in failed.text
    assert client.get("/health").status_code == 200
    monkeypatch.setattr(app.ingestion, "write_manifest", real_write)
    assert _upload(client, demo_deck).status_code == 200


def test_provider_client_construction_failure_degrades(
    make_settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Real clients are built when not injected; a construction failure is degraded, not fake."""

    def refuse(settings):
        raise httpx.InvalidURL("Invalid IPv4 address")

    monkeypatch.setattr(app.main, "build_embeddings", refuse)
    with TestClient(create_app(make_settings(key=TEST_PLACEHOLDER_KEY))) as client:
        health = client.get("/health")
        assert health.status_code == 503
        assert health.json()["reasons"] == ["provider_client_unavailable"]
        assert client.post("/ask", data={"question": "q"}).status_code == 503
