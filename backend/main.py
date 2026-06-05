from fastapi import FastAPI
from redis import asyncio as aioredis
from qdrant_client import AsyncQdrantClient

from backend.config.settings import get_settings
from backend.webhook_receiver.router import router as webhook_router

app = FastAPI(title="prreview")

s = get_settings()
_redis = aioredis.from_url(s.redis_url, decode_responses=True)
_qdrant = AsyncQdrantClient(url=s.qdrant_url, api_key=s.qdrant_api_key)

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