from __future__ import annotations

from pydantic import BaseModel


class BackgroundRemovalRequest(BaseModel):
    image_id: str


class BackgroundRemovalResponse(BaseModel):
    image_id: str
    original_object_key: str
    processed_object_key: str
    status: str
