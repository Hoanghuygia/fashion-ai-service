from __future__ import annotations

from dataclasses import dataclass
import uuid

from app.modules.background_removal.schemas import (
    BackgroundRemovalRequest,
    BackgroundRemovalResult,
)


@dataclass(frozen=True)
class BackgroundRemovalService:
    repo: object
    storage: object
    processor: object

    def process(self, request: BackgroundRemovalRequest) -> BackgroundRemovalResult:
        attachment = self.repo.get_active_by_id(request.attachment_id)
        if attachment is None:
            raise ValueError("Attachment not found")

        original_bytes = self.storage.download(attachment.bucket, attachment.object_key)
        processed_bytes = self.processor.remove_background(original_bytes)
        processed_id = f"att_{uuid.uuid4().hex}"
        processed_object_key = f"{request.processed_prefix}/{processed_id}_nobg.png"
        processed_bucket = attachment.bucket

        self.storage.upload(
            processed_bucket,
            processed_object_key,
            processed_bytes,
            "image/png",
        )

        self.repo.create(
            id=processed_id,
            object_key=processed_object_key,
            bucket=processed_bucket,
            original_filename=None,
            content_type="image/png",
            size=len(processed_bytes),
            status="BACKGROUND_REMOVED",
            is_deleted=False,
            source_attachment_id=attachment.id,
        )
        self.repo.update_status(attachment.id, "BACKGROUND_REMOVED")

        return BackgroundRemovalResult(
            processed_attachment_id=processed_id,
            processed_bucket=processed_bucket,
            processed_object_key=processed_object_key,
        )
