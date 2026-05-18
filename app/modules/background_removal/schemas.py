from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BackgroundRemovalRequest:
    attachment_id: str
    processed_prefix: str


@dataclass(frozen=True)
class BackgroundRemovalResult:
    processed_attachment_id: str
    processed_bucket: str
    processed_object_key: str
