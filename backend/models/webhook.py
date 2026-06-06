"""Pydantic model for a parsed GitHub pull_request webhook payload."""

from pydantic import BaseModel, Field

from backend.models.enums import PullRequestAction


class Repository(BaseModel):
    full_name: str = Field(..., description="e.g. 'octocat/hello-world'")


class PullRequestRef(BaseModel):
    sha: str  # commit SHA at the tip of the branch


class PullRequest(BaseModel):
    number: int
    title: str
    body: str | None = None
    head: PullRequestRef
    base: PullRequestRef


class WebhookEvent(BaseModel):
    action: PullRequestAction
    pull_request: PullRequest
    repository: Repository