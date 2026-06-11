# backend/integrations/__init__.py
# Third-party integrations: GitHub REST API, Qdrant vector DB, etc.
#
# This package owns all code that talks to external systems.
# orchestrator/ never imports from here directly — it receives
# integration clients via dependency injection (settings).

from backend.integrations.github_client import (
    GitHubClient,
    GitHubAPIError,
    GitHubNotFoundError,
    GitHubRateLimitError,
)

__all__ = [
    "GitHubClient",
    "GitHubAPIError",
    "GitHubNotFoundError",
    "GitHubRateLimitError",
]