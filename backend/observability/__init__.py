"""Observability package: structured logging + workflow context."""

import logging

from backend.observability.workflow_context import (
    WorkflowContext,
    get_workflow_context,
    reset_workflow_context,
    set_workflow_context,
)


class WorkflowContextFilter(logging.Filter):
    """
    Stamps every LogRecord with workflow_id and agent_type read from the
    current ContextVar. Attach this filter to the root logger once at
    startup; every log line emitted thereafter carries the tag for free.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        ctx = get_workflow_context()
        record.workflow_id = ctx.workflow_id or "-"
        record.agent_type = ctx.agent_type
        return True


def install_workflow_context_filter() -> None:
    """Attach the filter to the root logger. Idempotent."""
    root = logging.getLogger()
    for f in root.filters:
        if isinstance(f, WorkflowContextFilter):
            return
    root.addFilter(WorkflowContextFilter())


__all__ = [
    "WorkflowContext",
    "WorkflowContextFilter",
    "get_workflow_context",
    "install_workflow_context_filter",
    "reset_workflow_context",
    "set_workflow_context",
]
