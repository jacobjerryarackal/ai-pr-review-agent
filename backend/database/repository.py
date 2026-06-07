import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import FindingRecord, PRReviewRecord

logger = logging.getLogger(__name__)

_SEVERITY_RANK: dict[str, int] = {
    "critical": 0, "high": 1, "medium": 2, "low": 3,
}


async def save_review(
    session: AsyncSession,
    *,
    review_id: str,
    repo_full_name: str,
    pr_number: int,
    pr_title: str,
    head_commit_sha: str,
    pr_diff: str,
    verdict: str | None,
    status: str,
    overall_confidence: float,
    needs_human_review: bool,
    human_review_reason: str,
    findings: list[dict[str, Any]],
    github_review_id: int | None = None,
) -> PRReviewRecord:
    now = datetime.now(timezone.utc)

    review = PRReviewRecord(
        id=review_id,
        repo_full_name=repo_full_name,
        pr_number=pr_number,
        pr_title=pr_title,
        head_commit_sha=head_commit_sha,
        diff_hash=PRReviewRecord.compute_diff_hash(pr_diff),
        verdict=verdict,
        status=status,
        overall_confidence=overall_confidence,
        needs_human_review=1 if needs_human_review else 0,
        human_review_reason=human_review_reason,
        github_review_id=github_review_id,
        created_at=now,
        updated_at=now,
    )

    finding_records = [
        FindingRecord(
            id=str(uuid.uuid4()),
            review_id=review_id,
            repo_full_name=repo_full_name,
            agent_type=f.get("agent_type", "unknown"),
            severity=f.get("severity", "low"),
            category=f.get("category", "quality"),
            summary=f.get("summary", ""),
            file_path=f.get("file_path"),
            line_start=f.get("line_start"),
            line_end=f.get("line_end"),
            suggestion=f.get("suggestion"),
            confidence=float(f.get("confidence", 0.5)),
            created_at=now,
        )
        for f in findings
    ]

    async with session.begin():
        session.add(review)
        session.add_all(finding_records)
        await session.flush()

    logger.info(
        "save_review | review_id=%s repo=%s pr=%d findings=%d status=%s",
        review_id, repo_full_name, pr_number, len(findings), status,
    )
    return review


async def get_review(session, review_id):
    result = await session.execute(
        select(PRReviewRecord).where(PRReviewRecord.id == review_id)
    )
    return result.scalar_one_or_none()


async def list_reviews(session, *, repo_full_name=None, status=None, limit=50, offset=0):
    conditions = []
    if repo_full_name is not None:
        conditions.append(PRReviewRecord.repo_full_name == repo_full_name)
    if status is not None:
        conditions.append(PRReviewRecord.status == status)

    count_result = await session.execute(
        select(func.count()).select_from(PRReviewRecord).where(*conditions)
    )
    total = count_result.scalar_one()

    data_result = await session.execute(
        select(PRReviewRecord).where(*conditions)
        .order_by(PRReviewRecord.created_at.desc())
        .limit(limit).offset(offset)
    )
    return list(data_result.scalars().all()), total


async def list_findings_for_repo(session, repo_full_name, min_severity="high", limit=100, offset=0):
    min_rank = _SEVERITY_RANK.get(min_severity.lower(), 1)
    included = [s for s, r in _SEVERITY_RANK.items() if r <= min_rank]
    if not included:
        return []
    result = await session.execute(
        select(FindingRecord)
        .where(
            FindingRecord.repo_full_name == repo_full_name,
            FindingRecord.severity.in_(included),
        )
        .order_by(FindingRecord.created_at.desc())
        .limit(limit).offset(offset)
    )
    return list(result.scalars().all())