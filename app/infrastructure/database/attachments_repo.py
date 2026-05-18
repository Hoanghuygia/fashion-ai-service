from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.infrastructure.database.models import Attachment


class AttachmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_active_by_id(self, attachment_id: str) -> Attachment | None:
        stmt = select(Attachment).where(
            Attachment.id == attachment_id, Attachment.is_deleted.is_(False)
        )
        attachment = self.session.execute(stmt).scalars().first()
        return attachment

    def create(
        self,
        *,
        id: str,
        object_key: str,
        bucket: str,
        original_filename: str | None,
        content_type: str | None,
        size: int | None,
        status: str | None,
        is_deleted: bool,
        source_attachment_id: str | None,
    ) -> Attachment:
        attachment = Attachment(
            id=id,
            object_key=object_key,
            bucket=bucket,
            original_filename=original_filename,
            content_type=content_type,
            size=size,
            status=status,
            is_deleted=is_deleted,
            source_attachment_id=source_attachment_id,
        )
        self.session.add(attachment)
        self.session.commit()
        self.session.refresh(attachment)
        return attachment

    def update_status(self, attachment_id: str, status: str) -> None:
        stmt = update(Attachment).where(Attachment.id == attachment_id).values(status=status)
        self.session.execute(stmt)
        self.session.commit()
