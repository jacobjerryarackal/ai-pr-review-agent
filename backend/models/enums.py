"""enums for fixed-set values."""

from enum import Enum


class WebhookEventType(str, Enum):
    PULL_REQUEST = "pull_request"


class PullRequestAction(str, Enum):
    OPENED = "opened"
    REOPENED = "reopened"
    SYNCHRONIZE = "synchronize"  # new commits pushed to PR branch
    CLOSED = "closed"
    EDITED = "edited"
    READY_FOR_REVIEW = "ready_for_review"