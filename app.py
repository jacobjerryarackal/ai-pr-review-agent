import os
from fastapi import FastAPI
from redis import asyncio as aioredis
from qdrant_client import AsyncQdrantClient

app = FastAPI(title="step-08-add-qdrant")

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")

_redis = aioredis.from_url(REDIS_URL, decode_responses=True)
_qdrant = AsyncQdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


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