"""backend/config/settings.py — adds database_url."""

from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    redis_url: str = Field(..., description="redis:// URL")
    qdrant_url: str = Field(..., description="HTTP URL of Qdrant")
    qdrant_api_key: Optional[str] = Field(default=None)
    github_webhook_secret: str = Field(..., description="HMAC shared secret")
    database_url: str = Field(
        ...,
        description="postgresql+asyncpg://... connection string. "
                    "Local: postgresql+asyncpg://postgres:postgres@postgres:5432/prreview "
                    "Cloud (Neon): use ?ssl=require, NOT ?sslmode=require",
    )
    port: int = Field(default=8000)


@lru_cache
def get_settings() -> Settings:
    return Settings()