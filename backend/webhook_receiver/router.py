"""router with HMAC validation + 401 on rejection."""

import logging

from fastapi import APIRouter, Header, HTTPException, Request, status

from backend.config.settings import get_settings
from backend.webhook_receiver.validator import (
    WebhookValidationError,
    validate_github_signature,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/github", status_code=status.HTTP_200_OK)
async def receive_github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
):
    raw_body = await request.body()
    settings = get_settings()

    try:
        validate_github_signature(
            payload_bytes=raw_body,
            signature_header=x_hub_signature_256,
            secret=settings.github_webhook_secret,
        )
    except WebhookValidationError as e:
        logger.warning("webhook signature rejected: %s", e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    logger.info("webhook validated: %d bytes", len(raw_body))
    return {"received": True, "bytes": len(raw_body)}
