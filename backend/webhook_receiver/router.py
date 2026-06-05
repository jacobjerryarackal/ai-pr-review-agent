"""
backend/webhook_receiver/router.py

Now reads the raw bytes of the incoming POST request. We need raw
bytes (not parsed JSON) because step 04 will validate an HMAC
signature over the EXACT bytes received — any reformat changes the
hash.
"""

import logging

from fastapi import APIRouter, Request, status

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/webhook",
    tags=["webhook"],
)


@router.post("/github", status_code=status.HTTP_200_OK)
async def receive_github_webhook(request: Request):
    """Read the raw body, log its size, return success."""
    raw_body = await request.body()
    logger.info("webhook received: %d bytes", len(raw_body))
    return {"received": True, "bytes": len(raw_body)}