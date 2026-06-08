import asyncio, logging
from backend.database import (
    create_all_tables, get_review, get_sessionmaker,
    list_reviews, save_review,
)
from backend.observability import (
    install_workflow_context_filter,
    reset_workflow_context, set_workflow_context,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | wf=%(workflow_id)s agent=%(agent_type)s | %(message)s",
)
install_workflow_context_filter()
log = logging.getLogger("seed")


async def main():
    await create_all_tables()

    workflow_id = "octocat/hello-world:42:abc1234"
    review_id = workflow_id  # for the demo, identical
    sm = get_sessionmaker()

    token = set_workflow_context(workflow_id=workflow_id, agent_type="seed")
    try:
        async with sm() as session:
            review = await save_review(
                session=session,
                review_id=review_id,
                repo_full_name="octocat/hello-world",
                pr_number=42,
                pr_title="demo: prove the wiring is alive",
                head_commit_sha="abc1234",
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