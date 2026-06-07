import hashlib
from datetime import datetime, timezone

from sqlalchemy import BigInteger, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.postgres import Base


class PRReviewRecord(Base):
    """
    One row per completed PR review.

    Identity: `id` is a UUID string we generate in the orchestrator. We do not
    use a database-generated integer because reviews can be created by
    multiple worker processes — UUIDs avoid coordination.
    """

    __tablename__ = "pr_review_records"

    # ---- identity ----------------------------------------------------------
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # ---- which PR this is --------------------------------------------------
    repo_full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    pr_number: Mapped[int] = mapped_column(Integer, nullable=False)
    pr_title: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    head_commit_sha: Mapped[str] = mapped_column(String(64), nullable=False)

    # diff_hash — stable fingerprint of the diff text, used for idempotency.
    # Two webhook deliveries for the same commit produce the same diff_hash,
    # so we can detect "already reviewed this exact diff" cheaply.
    diff_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # github_review_id — the integer ID GitHub returns when we POST a review.
    # CRITICAL: BigInteger, NOT Integer.
    # GitHub review IDs crossed 2,147,483,647 (max signed INT4) in 2024 —
    # any code using Integer here started crashing at insert time.
    # See docs/war-stories/bigint-github-review-id.md for the long version.
    # Nullable because HITL-routed reviews are never posted to GitHub
    # (so we have no GitHub-side ID for them).
    github_review_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # ---- result ------------------------------------------------------------
    # verdict: "approve" | "request_changes" | "needs_human_review" | None
    verdict: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="received")
    overall_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # HITL routing flags
    needs_human_review: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    human_review_reason: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # ---- timestamps --------------------------------------------------------
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Composite index: when we list reviews per repo ordered by date, this is
    # the access path. Postgres will use it for `WHERE repo_full_name=? ORDER BY created_at DESC`.
    __table_args__ = (
        Index("ix_pr_review_repo_created", "repo_full_name", "created_at"),
    )

    @staticmethod
    def compute_diff_hash(diff_text: str) -> str:
        """SHA-256 of the diff bytes; used for idempotency."""
        return hashlib.sha256(diff_text.encode("utf-8")).hexdigest()