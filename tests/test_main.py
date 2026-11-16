"""Route and settings tests (offline; injected settings, no network)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import ConfigError, contained, load_settings
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


def test_contained_rejects_escape(data_dir: Path) -> None:
    with pytest.raises(ConfigError):
        contained(data_dir, "..", "outside")
