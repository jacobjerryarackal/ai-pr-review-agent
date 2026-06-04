import os
from fastapi import FastAPI
from redis import asyncio as aioredis

app = FastAPI(title="step-07-add-redis")

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
_redis = aioredis.from_url(REDIS_URL, decode_responses=True)


@app.get("/health/live")
async def liveness():
    return {"status": "ok"}


@app.get("/health/redis")
async def redis_health():
    pong = await _redis.ping()
    return {"redis": "ok" if pong else "down"}
