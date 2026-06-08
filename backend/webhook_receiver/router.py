"""
backend/webhook_receiver/router.py

Final shape (for Phase 3): validate, filter, dedupe, parse,
ENQUEUE, return fast.
"""

import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from backend.config.settings import Settings, get_settings
from backend.core.exceptions import WebhookParseError, WebhookValidationError
from backend.job_queue.arq_worker import enqueue_review_job
from backend.observability import reset_workflow_context, set_workflow_context
from backend.webhook_receiver.parser import parse_pull_request_event
from backend.webhook_receiver.validator import validate_github_signature

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])

_seen_delivery_ids: set[str] = set()


def _is_duplicate_delivery(delivery_id: str | None) -> bool:
    if delivery_id is None:
        return False
    if delivery_id in _seen_delivery_ids:
        return True
    _seen_delivery_ids.add(delivery_id)
    return False


@router.post("/github", status_code=status.HTTP_200_OK)
async def receive_github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
    x_github_delivery: str | None = Header(default=None),
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

    if _is_duplicate_delivery(x_github_delivery):
        logger.info("duplicate delivery: %s", x_github_delivery)
        return {"received": True, "duplicate": True, "delivery_id": x_github_delivery}

    try:
        event = parse_pull_request_event(raw_body)
    except WebhookParseError as e:
        logger.warning("parse failed: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    workflow_id = (
        f"{event.repository.full_name}:{event.pull_request.number}:"
        f"{event.pull_request.head.sha}"
    )
    token = set_workflow_context(workflow_id=workflow_id, agent_type="webhook")
    try:
        job_id = await enqueue_review_job(event)
    finally:
        reset_workflow_context(token)

    logger.info(
        "PR #%d (%s) on %s — action=%s, delivery=%s, job=%s",
        event.pull_request.number,
        event.pull_request.title,
        event.repository.full_name,
        event.action.value,
        x_github_delivery,
        job_id,
    )
    return {
        "received": True,
        "repo": event.repository.full_name,
        "pr": event.pull_request.number,
        "action": event.action.value,
        "delivery_id": x_github_delivery,
        "job_id": job_id,
        "workflow_id": workflow_id,
    }
