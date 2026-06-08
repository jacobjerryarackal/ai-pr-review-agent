# backend/database/postgres.py
#
# Async SQLAlchemy engine + ORM Base + per-request session factory.

import logging
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
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
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = _build_engine()
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """
    Build (lazily) the session factory bound to our engine.

    A "sessionmaker" is exactly what it sounds like: a factory.
    Call it as `async with sessionmaker() as session:` and you get
    a fresh AsyncSession for one logical unit of work (one request,
    one job, one test).
    """
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,  # don\'t auto-expire ORM objects after commit
            autoflush=False,         # we control when SQL hits the wire
        )
    return _sessionmaker


# ---------------------------------------------------------------------------
# get_db — FastAPI dependency
#
# Inside a route handler:
#     async def my_route(db: AsyncSession = Depends(get_db)): ...
#
# FastAPI calls get_db() before the route runs, holds the yielded session
# while the route runs, then runs the rest of get_db() after the route
# returns — closing the session and returning the connection to the pool.
#
# That is the whole point of `yield` here: it splits the function into
# "before the route" (build the session) and "after the route" (close it).
# ---------------------------------------------------------------------------
async def get_db() -> AsyncIterator[AsyncSession]:
    sm = get_sessionmaker()
    async with sm() as session:
        yield session


# ---------------------------------------------------------------------------
# create_all_tables() — startup-time schema sync
#
# Reads every ORM class registered with Base.metadata and emits CREATE TABLE
# (and CREATE INDEX) statements for any tables that don't exist yet. Existing
# tables are left alone — create_all is idempotent.
#
# We deliberately do NOT use Alembic in this codebase (ADR-005). For a
# single-team, single-environment project iterating fast, create_all on
# startup is honest about the constraint: no schema versioning, no rollback,
# adds-only migrations.
# ---------------------------------------------------------------------------
async def create_all_tables() -> None:
    """Create all tables registered with Base.metadata. Idempotent."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
