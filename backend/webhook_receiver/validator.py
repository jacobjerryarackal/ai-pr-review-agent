import hashlib
import hmac


class WebhookValidationError(Exception):
    """Raised when a webhook signature is missing or wrong."""


def validate_github_signature(
    payload_bytes: bytes,
    signature_header: str | None,
    secret: str,
) -> None:
    """Validate the X-Hub-Signature-256 header. Raises on failure."""
    if signature_header is None:
        raise WebhookValidationError("missing X-Hub-Signature-256 header")

    if not signature_header.startswith("sha256="):
        raise WebhookValidationError("malformed signature header (no sha256= prefix)")

    received_hex = signature_header.removeprefix("sha256=")

    expected_hex = hmac.new(
        key=secret.encode("utf-8"),
        msg=payload_bytes,
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(received_hex, expected_hex):
        raise WebhookValidationError("signature mismatch")