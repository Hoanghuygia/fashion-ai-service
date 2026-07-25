from __future__ import annotations

import uuid
from types import TracebackType
from typing import Protocol

from app.modules.background_removal.rembg_processor import ImageTooLargeError, RembgProcessor
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


class UnitOfWork(Protocol):
    attachments: AttachmentRepository

    def __enter__(self) -> UnitOfWork: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class StorageClient(Protocol):
    def download(self, bucket: str, object_key: str) -> bytes: ...

    def upload(self, bucket: str, object_key: str, data: bytes, content_type: str) -> None: ...


class BackgroundRemovalService:
    def __init__(
        self,
        storage_client: StorageClient,
        uow: UnitOfWork,
    ) -> None:
        self.storage = storage_client
        self.uow = uow
        self.processor = RembgProcessor()

    def remove_background(self, image_id: str, processed_prefix: str) -> BackgroundRemovalResponse:
        with self.uow as uow:
            attachment = uow.attachments.get_active_by_id(image_id)
            if attachment is None:
                raise BackgroundRemovalError("NOT_FOUND")

            # Capture what we need before the transaction closes; ORM instances
            # expire on commit and detach when the session closes.
            source_id = attachment.id
            source_object_key = attachment.object_key
            bucket = attachment.bucket
            original_filename = attachment.original_filename

            original_bytes = self.storage.download(bucket, source_object_key)
            try:
                processed_bytes = self.processor.remove_background(original_bytes)
            except ImageTooLargeError as exc:
                raise BackgroundRemovalError("IMAGE_TOO_LARGE") from exc

            processed_id = f"att_{uuid.uuid4().hex}"
            processed_object_key = f"{processed_prefix}{processed_id}_nobg.png"

            # NOTE: object storage is not transactional. If commit fails after
            # this upload, the processed object is orphaned in S3 (acceptable;
            # a later cleanup/GC job can reconcile).
            self.storage.upload(bucket, processed_object_key, processed_bytes, "image/png")

            uow.attachments.create(
                id=processed_id,
                object_key=processed_object_key,
                bucket=bucket,
                original_filename=original_filename,
                content_type="image/png",
                size=len(processed_bytes),
                status="BACKGROUND_REMOVED",
                is_deleted=False,
                source_attachment_id=source_id,
            )
            uow.attachments.update_status(source_id, "BACKGROUND_REMOVED")
            uow.commit()

        return BackgroundRemovalResponse(
            image_id=source_id,
            original_object_key=source_object_key,
            processed_object_key=processed_object_key,
            status="BACKGROUND_REMOVED",
        )
