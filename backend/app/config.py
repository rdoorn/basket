"""Application configuration loaded from the environment."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the Basket API."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mongo_url: str = "mongodb://mongo:47017"
    mongo_db: str = "basket"
    api_port: int = 18420


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance (built once per process)."""
    return Settings()
