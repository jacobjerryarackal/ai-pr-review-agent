# backend/integrations/github_client.py
#
# Async GitHub REST API client.
#
# THE ONLY PLACE IN THE CODEBASE THAT TALKS TO GITHUB.
#
# Public API (what the orchestrator uses):
#   client = GitHubClient(settings)
#   metadata = await client.get_pr_metadata(repo, pr_number)
#   diff     = await client.get_pr_diff(repo, pr_number)
#   files    = await client.get_pr_files(repo, pr_number)
#   response = await client.post_pr_review(repo, pr_number, payload)  # Phase 8

import asyncio
import logging
from typing import Any

import httpx

from backend.config.settings import Settings

logger = logging.getLogger(__name__)

# =============================================================================
# TIMEOUT CONFIGURATION
#
# WIKI: release-it / Timeouts.md
#   "It is essential that any resource pool that blocks threads must have a
#    timeout to ensure threads are eventually unblocked."
#
# We set FOUR separate timeouts (httpx supports all four independently):
#   connect  — how long to wait for the TCP connection to be established
#   read     — how long to wait for the server to start sending response bytes
#   write    — how long to wait to send our request body (POST review payload)
#   pool     — how long to wait for an available connection from the pool
#
# These values are conservative defaults. They can be tuned in production
# via environment variables when we add observability (Phase 10).
# =============================================================================

_TIMEOUT = httpx.Timeout(
    connect=5.0,   # TCP handshake: 5s is generous for api.github.com
    read=30.0,     # Reading diffs: 30s handles even 10MB diffs
    write=10.0,    # Posting review payloads (inline comments)
    pool=5.0,      # Waiting for a connection from the pool
)

class GitHubClient:
    """
    Async client for the GitHub REST API.

    LIFECYCLE:
      Instantiate once per PR review workflow. Do not share across concurrent
      reviews — that would create shared state and complicate error handling.

      Usage in build_context node:
        client = GitHubClient(settings)
        try:
            metadata = await client.get_pr_metadata(repo, pr_number)
            diff = await client.get_pr_diff(repo, pr_number)
            files = await client.get_pr_files(repo, pr_number)
        finally:
            await client.close()

      OR use as an async context manager:
        async with GitHubClient(settings) as client:
            diff = await client.get_pr_diff(repo, pr_number)

    WIKI: Stability-Antipatterns.md
      "No global state" — this client is instantiated explicitly.
      Never do: github_client = GitHubClient(get_settings()) at module level.
      That would bind settings at import time (breaks tests) and create a
      long-lived connection pool shared across all concurrent reviews.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Creates the client. Does NOT open any network connections yet.
        Connections are made on the first API call (lazy connect).

        settings.github_token    -> Authorization header value
        settings.github_api_base_url -> allows GitHub Enterprise + mock in tests
        """
        self._token = settings.github_token
        self._base_url = settings.github_api_base_url.rstrip("/")

        # The underlying HTTPX async client.
        # httpx.AsyncClient maintains a connection pool internally.
        # We set default headers here so every request includes them automatically.
        #
        # WIKI: Operations-Patterns.md "Trust, but verify."
        # We set Accept: application/vnd.github+json to pin the GitHub API version.
        # Without this, GitHub might return a different format in the future.
        self._http = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",  # pin to stable version
                "User-Agent": "ai-pr-review-agent/1.0",  # GitHub requires User-Agent
            },
            timeout=_TIMEOUT,
            # Follow redirects (GitHub sometimes redirects e.g. org renames)
            follow_redirects=True,
        )

        logger.debug(
            "github_client | init | base_url=%s",
            self._base_url,
        )

    async def close(self) -> None:
        """
        Closes the underlying HTTPX connection pool.

        ALWAYS call this when done with the client (or use as async context manager).
        Not closing leaks file descriptors and can cause ResourceWarning in tests.
        """
        await self._http.aclose()

    async def __aenter__(self) -> "GitHubClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()