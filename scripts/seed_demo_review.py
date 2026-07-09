import asyncio, logging

class WorkflowContextFilter(logging.Filter):
    def filter(self, record):
        try:
            from backend.observability.workflow_context import get_workflow_context
            ctx = get_workflow_context()
            record.workflow_id = ctx.workflow_id or "none"
            record.agent_type = ctx.agent_type or "system"
        except Exception:
            record.workflow_id = "none"
            record.agent_type = "system"
        return True

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | wf=%(workflow_id)s agent=%(agent_type)s | %(message)s",
)
for handler in logging.getLogger().handlers:
    handler.addFilter(WorkflowContextFilter())
log = logging.getLogger("seed")

from backend.database.postgres import create_all_tables, get_session_factory
from backend.database.repository import get_review, list_reviews, save_review
from backend.observability.workflow_context import (
    reset_workflow_context, set_workflow_context,
)


async def main():
    await create_all_tables()

    import time
    timestamp_sha = f"abc{int(time.time())}"
    workflow_id = f"octocat/hello-world:42:{timestamp_sha}"
    review_id = workflow_id  # for the demo, identical
    sm = get_session_factory()

    token = set_workflow_context(workflow_id=workflow_id, agent_type="seed")
    try:
        async with sm() as session:
            review = await save_review(
                session=session,
                review_id=review_id,
                repo_full_name="octocat/hello-world",
                pr_number=42,
                pr_title="demo: prove the wiring is alive",
                head_commit_sha=timestamp_sha,
                pr_diff="diff --git a/x b/x\n+hello\n",
                verdict="approve",
                status="completed",
                overall_confidence=0.91,
                needs_human_review=False,
                human_review_reason="",
                findings=[
                    {"agent_type": "security", "severity": "high",
                     "category": "security", "summary": "fake finding",
                     "confidence": 0.9},
                    {"agent_type": "quality", "severity": "medium",
                     "category": "quality", "summary": "another fake",
                     "confidence": 0.7},
                ],
                github_review_id=98765432109,
            )
            log.info("saved id=%s github_review_id=%s",
                     review.id, review.github_review_id)

            roundtrip = await get_review(session=session, review_id=review_id)
            log.info("roundtrip findings=%d verdict=%s",
                     len(roundtrip.findings), roundtrip.verdict)

            rows, total = await list_reviews(
                session=session, repo_full_name="octocat/hello-world"
            )
            log.info("list_reviews | rows=%d total=%d", len(rows), total)
    finally:
        reset_workflow_context(token)


if __name__ == "__main__":
    asyncio.run(main())