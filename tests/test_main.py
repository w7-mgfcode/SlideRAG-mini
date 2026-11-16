"""Route and settings tests (offline; injected settings, no network)."""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import ConfigError, Settings, contained, load_settings
from app.main import create_app
from conftest import TEST_PLACEHOLDER_KEY


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
        ("LLM_BASE_URL", "https://bad host.invalid/v1"),
        ("LLM_BASE_URL", "https://bad_host.invalid/v1"),
        ("EMBEDDING_BASE_URL", "https://a..b.invalid/v1"),
        ("EMBEDDING_BASE_URL", "https://-a.invalid/v1"),
        ("EMBEDDING_BASE_URL", "https://ex\u00e4mple.invalid/v1"),
        ("DATA_DIR", "/"),
    ],
)
def test_load_settings_rejects_unsafe_values(name: str, value: str, data_dir: Path) -> None:
    with pytest.raises(ConfigError):
        load_settings({"DATA_DIR": str(data_dir), name: value})


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
