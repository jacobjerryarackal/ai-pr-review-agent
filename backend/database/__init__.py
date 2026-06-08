"""Database layer: engine, sessions, ORM models, repository functions."""

from backend.database.models import FindingRecord, PRReviewRecord
from backend.database.postgres import (
    Base,
    create_all_tables,
    get_db,
    get_engine,
    get_sessionmaker,
)
from backend.database.repository import (
    get_review,
    list_findings_for_repo,
    list_reviews,
    save_review,
)

__all__ = [
    "Base",
    "create_all_tables",
    "get_db",
    "get_engine",
    "get_sessionmaker",
    "PRReviewRecord",
    "FindingRecord",
    "save_review",
    "get_review",
    "list_reviews",
    "list_findings_for_repo",
]
