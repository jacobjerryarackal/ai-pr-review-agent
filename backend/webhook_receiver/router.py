"""router with proper dependency injection."""

import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from backend.config.settings import Settings, get_settings
from backend.core.exceptions import WebhookParseError, WebhookValidationError
from backend.webhook_receiver.parser import parse_pull_request_event
from backend.webhook_receiver.validator import validate_github_signature

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/github", status_code=status.HTTP_200_OK)
async def receive_github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
):
    raw_body = await request.body()

    try:
        validate_github_signature(
            payload_bytes=raw_body,
            signature_header=x_hub_signature_256,
            secret=settings.github_webhook_secret,
        )
    except WebhookValidationError as e:
        logger.warning("webhook signature rejected: %s", e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    if x_github_event != "pull_request":
        logger.info("ignoring event type: %s", x_github_event)
        return {"received": True, "ignored": True, "event": x_github_event}

    try:
        event = parse_pull_request_event(raw_body)
    except WebhookParseError as e:
        logger.warning("parse failed: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    logger.info(
        "PR #%d (%s) on %s — action=%s",
        event.pull_request.number,
        event.pull_request.title,
        event.repository.full_name,
        event.action.value,
    )
    return {
        "received": True,
        "repo": event.repository.full_name,
        "pr": event.pull_request.number,
        "action": event.action.value,
    }