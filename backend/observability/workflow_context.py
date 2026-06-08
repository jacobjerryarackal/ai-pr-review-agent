from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class WorkflowContext:
    workflow_id: Optional[str]
    agent_type: str    # "security", "quality", "system", etc.


_DEFAULT = WorkflowContext(workflow_id=None, agent_type="system")

_current: ContextVar[WorkflowContext] = ContextVar(
    "ai_pr_review_workflow_context",
    default=_DEFAULT,
)


def get_workflow_context() -> WorkflowContext:
    """Read the current context. Always returns a value (default if unset)."""
    return _current.get()


def set_workflow_context(*, workflow_id: Optional[str], agent_type: str) -> Token:
    """
    Push a new context onto the stack. Returns a token to pass to reset().
    """
    return _current.set(
        WorkflowContext(workflow_id=workflow_id, agent_type=agent_type)
    )


def reset_workflow_context(token: Token) -> None:
    """Restore the previous context."""
    _current.reset(token)
