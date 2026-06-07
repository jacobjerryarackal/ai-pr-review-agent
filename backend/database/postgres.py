# backend/database/postgres.py
#
# Async SQLAlchemy engine + ORM Base.

import logging

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase

from backend.config.settings import get_settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models (SQLAlchemy 2.0 style)."""
    pass


def _build_engine():
    cfg = get_settings()

    engine = create_async_engine(
        cfg.database_url,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
        echo=False,
    )

    safe_host = cfg.database_url.split("@")[-1] if "@" in cfg.database_url else "<no-host>"
    logger.info("postgres engine built | host=%s", safe_host)
    return engine


_engine = None


def get_engine():
    """Return the module-level engine, building it on first call."""
    global _engine
    if _engine is None:
        _engine = _build_engine()
    return _engine