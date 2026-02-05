import pytest
from app.core.config import Settings


def test_settings_loads_from_env(monkeypatch):
    """Test that settings correctly loads from environment variables"""
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    monkeypatch.setenv("PLAID_CLIENT_ID", "test_client")
    monkeypatch.setenv("PLAID_SECRET", "test_secret")
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "test_maps")
    monkeypatch.setenv("GOOGLE_PLACES_API_KEY", "test_places")
    monkeypatch.setenv("ENCRYPTION_KEY", "test_encryption")

    settings = Settings()

    assert settings.GEMINI_API_KEY == "test_key"
    assert settings.PLAID_CLIENT_ID == "test_client"
    assert settings.PLAID_SECRET == "test_secret"


def test_settings_validates_required_fields(monkeypatch):
    """Test that missing required fields raise validation error"""
    required = (
        "GEMINI_API_KEY", "PLAID_CLIENT_ID", "PLAID_SECRET",
        "GOOGLE_MAPS_API_KEY", "GOOGLE_PLACES_API_KEY", "ENCRYPTION_KEY",
    )
    for key in required:
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(Exception):
        Settings()
