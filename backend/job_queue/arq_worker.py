"""
backend/job_queue/arq_worker.py

ARQ-style job enqueue. Stub for Phase 3; real impl in Phase 4.
"""

import logging
import uuid

from backend.models.webhook import WebhookEvent

logger = logging.getLogger(__name__)


async def enqueue_review_job(event: WebhookEvent) -> str:
    """Enqueue a PR review job. Returns the job ID. (Stub for now.)"""
    job_id = f"stub-{uuid.uuid4().hex[:8]}"
    logger.info(
        "ENQUEUE STUB: review job %s for %s PR #%d (action=%s)",
        job_id,
        event.repository.full_name,
        event.pull_request.number,
        event.action.value,
    )
    return job_id