from __future__ import annotations

import uuid
from typing import Protocol

from app.modules.background_removal.rembg_processor import RembgProcessor
from app.modules.background_removal.schemas import BackgroundRemovalResponse


class BackgroundRemovalError(Exception):
    pass


class Attachment(Protocol):
    id: str
    object_key: str
    bucket: str
    original_filename: str | None


class AttachmentRepository(Protocol):
    def get_active_by_id(self, attachment_id: str) -> Attachment | None: ...

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
    ) -> Attachment: ...

    def update_status(self, attachment_id: str, status: str) -> None: ...


class StorageClient(Protocol):
    def download(self, bucket: str, object_key: str) -> bytes: ...

    def upload(self, bucket: str, object_key: str, data: bytes, content_type: str) -> None: ...


class BackgroundRemovalService:
    def __init__(
        self,
        storage_client: StorageClient,
        attachments_repo: AttachmentRepository,
    ) -> None:
        self.storage = storage_client
        self.repo = attachments_repo
        self.processor = RembgProcessor()

    def remove_background(self, image_id: str, processed_prefix: str) -> BackgroundRemovalResponse:
        attachment = self.repo.get_active_by_id(image_id)
        if attachment is None:
            raise BackgroundRemovalError("NOT_FOUND")

        original_bytes = self.storage.download(attachment.bucket, attachment.object_key)
        processed_bytes = self.processor.remove_background(original_bytes)

        processed_id = f"att_{uuid.uuid4().hex}"
        processed_object_key = f"{processed_prefix}{processed_id}_nobg.png"

        self.storage.upload(
            attachment.bucket,
            processed_object_key,
            processed_bytes,
            "image/png",
        )

        self.repo.create(
            id=processed_id,
            object_key=processed_object_key,
            bucket=attachment.bucket,
            original_filename=attachment.original_filename,
            content_type="image/png",
            size=len(processed_bytes),
            status="BACKGROUND_REMOVED",
            is_deleted=False,
            source_attachment_id=attachment.id,
        )
        self.repo.update_status(attachment.id, "BACKGROUND_REMOVED")

        return BackgroundRemovalResponse(
            image_id=attachment.id,
            original_object_key=attachment.object_key,
            processed_object_key=processed_object_key,
            status="BACKGROUND_REMOVED",
        )
