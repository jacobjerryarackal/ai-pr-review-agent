"""Webhook payload parser; uses central exceptions module."""

import json
import logging

from pydantic import ValidationError

from backend.core.exceptions import WebhookParseError
from backend.models.webhook import WebhookEvent

logger = logging.getLogger(__name__)


def parse_pull_request_event(raw_body: bytes) -> WebhookEvent:
    try:
        payload_dict = json.loads(raw_body)
    except json.JSONDecodeError as e:
        raise WebhookParseError(f"body is not valid JSON: {e}") from e

    try:
        return WebhookEvent.model_validate(payload_dict)
    except ValidationError as e:
        raise WebhookParseError(f"payload does not match schema: {e}") from e