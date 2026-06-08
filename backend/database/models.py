import hashlib
from datetime import datetime, timezone

from sqlalchemy import BigInteger, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    # ---- relationship to findings -----------------------------------------
    # selectin loading: when we fetch a PRReviewRecord, SQLAlchemy issues a
    # second query (SELECT ... WHERE review_id IN (...)) to pull all child
    # findings in one batch. Avoids N+1 queries when listing reviews.
    findings: Mapped[list["FindingRecord"]] = relationship(
        "FindingRecord",
        back_populates="review",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_pr_review_repo_created", "repo_full_name", "created_at"),
    )

    @staticmethod
    def compute_diff_hash(diff_text: str) -> str:
        """SHA-256 of the diff bytes; used for idempotency."""
        return hashlib.sha256(diff_text.encode("utf-8")).hexdigest()


class FindingRecord(Base):
    """
    One row per finding produced by a sub-agent (security/quality/test/docs).
    Many findings per review.
    """

    __tablename__ = "finding_records"

    # identity
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # foreign key back to the parent review
    review_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("pr_review_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # denormalized — copy of review.repo_full_name. Why? The hot analytical
    # query "give me all HIGH+ findings for repo X" should not need to JOIN
    # against pr_review_records every time. Copying the column trades a tiny
    # bit of storage and a small write-time cost for very fast reads.
    # (Storage-Engines wiki: "denormalize for the read pattern you actually
    #  have, not the read pattern you might one day have.")
    repo_full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # which agent produced it: "security" | "quality" | "test_coverage" | "documentation"
    agent_type: Mapped[str] = mapped_column(String(32), nullable=False)

    # finding shape
    severity: Mapped[str] = mapped_column(String(16), nullable=False)   # "critical" | "high" | "medium" | "low"
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    line_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    line_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    review: Mapped["PRReviewRecord"] = relationship(
        "PRReviewRecord",
        back_populates="findings",
    )

    __table_args__ = (
        # Composite index for the hot analytical query:
        #   WHERE repo_full_name = ? AND severity IN ('critical', 'high')
        # repo_full_name first (high cardinality) prunes the table; severity
        # filters the slice. Index seek instead of full table scan.
        Index("ix_finding_repo_severity", "repo_full_name", "severity"),
    )