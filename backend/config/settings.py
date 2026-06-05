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
    qdrant_url: str = Field(..., description="qdrant URL")
    github_webhook_secret: str = Field(..., description="HMAC shared secret")


@lru_cache
def get_settings() -> Settings:
    return Settings()