from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    object_key: Mapped[str] = mapped_column(String, nullable=False)
    bucket: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String, nullable=True)
    content_type: Mapped[str | None] = mapped_column(String, nullable=True)
    size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    source_attachment_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("attachments.id"),
        nullable=True,
    )
