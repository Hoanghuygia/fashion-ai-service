from sqlalchemy import Column, ForeignKey, Index, MetaData, String, Table, create_engine

from app.config import get_settings


def upgrade() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url, future=True)
    metadata = MetaData()
    attachments = Table("attachments", metadata, autoload_with=engine)
    if "source_attachment_id" not in attachments.c:
        Column("source_attachment_id", String, ForeignKey("attachments.id"), nullable=True).create(
            attachments
        )
    if "source_attachment_id" in attachments.c:
        Index("ix_attachments_source_attachment_id", attachments.c.source_attachment_id).create(
            bind=engine,
            checkfirst=True,
        )


def downgrade() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url, future=True)
    metadata = MetaData()
    attachments = Table("attachments", metadata, autoload_with=engine)
    if "source_attachment_id" in attachments.c:
        attachments.c.source_attachment_id.drop()
