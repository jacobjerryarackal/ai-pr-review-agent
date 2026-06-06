"""
backend/webhook_receiver/parser.py

Single responsibility: bytes + headers → typed WebhookEvent or raise.
"""

import json
import logging

from pydantic import ValidationError

from backend.models.webhook import WebhookEvent

logger = logging.getLogger(__name__)


class WebhookParseError(Exception):
    """Raised when the body is malformed or doesn't fit our schema."""


def parse_pull_request_event(raw_body: bytes) -> WebhookEvent:
    """Parse a pull_request webhook body into a typed WebhookEvent."""
    try:
        payload_dict = json.loads(raw_body)
    except json.JSONDecodeError as e:
        raise WebhookParseError(f"body is not valid JSON: {e}") from e

    try:
        return WebhookEvent.model_validate(payload_dict)
    except ValidationError as e:
        raise WebhookParseError(f"payload does not match schema: {e}") from e