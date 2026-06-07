import hashlib
from datetime import datetime, timezone

from sqlalchemy import Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.postgres import Base


class PRReviewRecord(Base):
    __tablename__ = "pr_review_records"

    # identity
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # which PR
    repo_full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    pr_number: Mapped[int] = mapped_column(Integer, nullable=False)
    pr_title: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    head_commit_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    diff_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # result
    verdict: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="received")
    overall_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    needs_human_review: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    human_review_reason: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # timestamps
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("ix_pr_review_repo_created", "repo_full_name", "created_at"),
    )

    @staticmethod
    def compute_diff_hash(diff_text: str) -> str:
        return hashlib.sha256(diff_text.encode("utf-8")).hexdigest()