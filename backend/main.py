"""
backend/main.py — the FastAPI app.

Step 10: introduce a `lifespan` context manager so we can run schema
sync (`create_all_tables`) on startup. Also wire a /health/postgres
endpoint that confirms the database is reachable.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text
from redis import asyncio as aioredis
from qdrant_client import AsyncQdrantClient

from backend.config.settings import get_settings
from backend.database.postgres import create_all_tables, get_engine
from backend.observability import install_workflow_context_filter
from backend.webhook_receiver.router import router as webhook_router


s = get_settings()
_redis = aioredis.from_url(s.redis_url, decode_responses=True)
_qdrant = AsyncQdrantClient(url=s.qdrant_url, api_key=s.qdrant_api_key)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once on startup, once on shutdown.

    Startup: create any missing tables (idempotent). No Alembic — see ADR-005.
    Shutdown: dispose the SQLAlchemy engine so connections drain cleanly.
    """
    install_workflow_context_filter()
    await create_all_tables()
    yield
    await get_engine().dispose()


app = FastAPI(title="prreview", lifespan=lifespan)
app.include_router(webhook_router)


@app.get("/health/live")
async def liveness():
    return {"status": "ok"}


@app.get("/health/redis")
async def redis_health():
    pong = await _redis.ping()
    return {"redis": "ok" if pong else "down"}


@app.get("/health/qdrant")
async def qdrant_health():
    collections = await _qdrant.get_collections()
    return {"qdrant": "ok", "collections": len(collections.collections)}


@app.get("/health/postgres")
async def postgres_health():
    """
    Cheap "can we talk to the database?" probe. Runs SELECT 1.
    If the engine cannot connect, this raises and FastAPI returns 500 —
    the right outcome for a health endpoint.
    """
    engine = get_engine()
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        value = result.scalar()
    return {"postgres": "ok", "select_one": value}
