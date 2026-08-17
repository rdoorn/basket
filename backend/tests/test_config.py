"""Tests for the application configuration module."""
from app.config import Settings


def test_defaults_use_non_obvious_ports():
    """Default settings expose the non-obvious ports and database name."""
    s = Settings(_env_file=None)
    assert "47017" in s.mongo_url
    assert s.api_port == 18420
    assert s.mongo_db == "basket"


def test_env_override(monkeypatch):
    """Environment variables override the default settings."""
    monkeypatch.setenv("API_PORT", "9999")
    s = Settings(_env_file=None)
    assert s.api_port == 9999
