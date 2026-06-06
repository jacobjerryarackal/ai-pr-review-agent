"""project-wide custom exceptions."""


class PRReviewError(Exception):
    """Base class for all custom exceptions in this project."""


class WebhookValidationError(PRReviewError):
    """Raised when an inbound webhook signature is missing or wrong."""


class WebhookParseError(PRReviewError):
    """Raised when a webhook body is malformed or off-schema."""