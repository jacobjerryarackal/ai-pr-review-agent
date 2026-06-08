import logging
from typing import Any

from backend.models.enums import ReviewStatus
from backend.orchestrator.state import PRReviewState

logger = logging.getLogger(__name__)


async def build_context(state: PRReviewState) -> dict[str, Any]:
    """
    Fetches the PR diff, file list, and metadata from GitHub.

    PHASE 5 STUB: Returns the stub data that's already in state.
    The graph structure is real — only the GitHub calls are stubbed.
    """
    logger.info(
        "build_context | workflow_id=%s | repo=%s pr=%d",
        state["workflow_id"],
        state["repo_full_name"],
        state["pr_number"],
    )

    return {
        "pr_diff": state.get("pr_diff", "# stubbed diff - Phase 5"),
        "changed_files": [],  # Empty stub — needs GitHub API in Phase 7
        "retrieved_context": "",  # Empty — RAG doesn't exist yet (Phase 6)
        "pr_title": state.get("pr_title", ""),
        "pr_body": state.get("pr_body", ""),
        "author_login": state.get("author_login", ""),
        "head_commit_sha": state.get("head_commit_sha", ""),
        "base_branch": state.get("base_branch", "main"),
        "status": ReviewStatus.IN_PROGRESS,
    }