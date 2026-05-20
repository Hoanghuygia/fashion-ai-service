from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.database.attachments_repo import AttachmentRepository
from app.infrastructure.database.models import Base
from app.modules.background_removal.schemas import BackgroundRemovalResponse
from app.modules.background_removal.service import BackgroundRemovalService


@pytest.fixture()
def session() -> Iterator[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    with SessionLocal() as db:
        yield db


def test_attachment_repo_create_and_get(session: Session) -> None:
    repo = AttachmentRepository(session)
    created = repo.create(
        id="att_1",
        object_key="raw/test.png",
        bucket="style-engine",
        original_filename="test.png",
        content_type="image/png",
        size=123,
        status="UPLOADED",
        is_deleted=False,
        source_attachment_id=None,
    )

    loaded = repo.get_active_by_id("att_1")

    assert loaded is not None
    assert created.id == loaded.id
    assert bool(loaded.is_deleted) is False


def test_migration_placeholder() -> None:
    assert True


def test_storage_client_builds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("S3_ENDPOINT", "http://localhost:9000")
    monkeypatch.setenv("S3_ACCESS_KEY", "test-access")
    monkeypatch.setenv("S3_SECRET_KEY", "test-secret")
    monkeypatch.setenv("S3_BUCKET", "style-engine-test")
    monkeypatch.setenv("S3_REGION", "us-west-2")
    monkeypatch.setenv("S3_USE_SSL", "false")
    monkeypatch.setenv("S3_PATH_STYLE", "true")

    from app.config import get_settings
    from app.infrastructure.storage.s3_client import StorageClient

    get_settings.cache_clear()
    settings = get_settings()

    client = StorageClient.build()
    s3_client = cast(Any, client.client)

    assert client.bucket == settings.s3_bucket
    assert s3_client.meta.region_name == settings.s3_region
    assert s3_client.meta.endpoint_url == settings.s3_endpoint
    assert s3_client.meta.config.s3["addressing_style"] == "path"


@dataclass
class FakeAttachment:
    id: str
    object_key: str
    bucket: str
    original_filename: str | None
    content_type: str | None
    size: int | None
    status: str | None
    is_deleted: bool
    source_attachment_id: str | None


class FakeAttachmentRepo:
    def __init__(self) -> None:
        self._items: dict[str, FakeAttachment] = {}
        self.created_ids: list[str] = []

    def get_active_by_id(self, attachment_id: str) -> FakeAttachment | None:
        item = self._items.get(attachment_id)
        if item is None or item.is_deleted:
            return None
        return item

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
    ) -> FakeAttachment:
        attachment = FakeAttachment(
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
        self._items[id] = attachment
        self.created_ids.append(id)
        return attachment

    def update_status(self, attachment_id: str, status: str) -> None:
        self._items[attachment_id].status = status


class FakeStorageClient:
    def __init__(self) -> None:
        self.downloads: list[tuple[str, str]] = []
        self.uploads: list[tuple[str, str, bytes, str]] = []
        self.objects: dict[tuple[str, str], bytes] = {}

    def download(self, bucket: str, object_key: str) -> bytes:
        self.downloads.append((bucket, object_key))
        return self.objects[(bucket, object_key)]

    def upload(self, bucket: str, object_key: str, data: bytes, content_type: str) -> None:
        self.uploads.append((bucket, object_key, data, content_type))
        self.objects[(bucket, object_key)] = data


def test_service_returns_processed_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.modules.background_removal.rembg_processor import RembgProcessor

    repo = FakeAttachmentRepo()
    storage = FakeStorageClient()
    original = repo.create(
        id="att_1",
        object_key="raw/test.png",
        bucket="style-engine",
        original_filename="test.png",
        content_type="image/png",
        size=123,
        status="UPLOADED",
        is_deleted=False,
        source_attachment_id=None,
    )
    storage.objects[(original.bucket, original.object_key)] = b"raw-bytes"

    monkeypatch.setattr(RembgProcessor, "remove_background", lambda self, data: b"processed")

    service = BackgroundRemovalService(storage, repo)
    result = service.remove_background(
        image_id=original.id,
        processed_prefix="processed/",
    )

    assert result.processed_object_key.startswith("processed/")
    assert result.processed_object_key.endswith("_nobg.png")
    assert result.status == "BACKGROUND_REMOVED"
    updated_original = repo.get_active_by_id(original.id)
    assert updated_original is not None
    assert updated_original.status == "BACKGROUND_REMOVED"

    processed = repo.get_active_by_id(repo.created_ids[-1])
    assert processed is not None
    assert processed.source_attachment_id == original.id
    assert processed.object_key == result.processed_object_key
    assert processed.status == "BACKGROUND_REMOVED"
    assert processed.content_type == "image/png"
    assert processed.size == len(b"processed")

    assert storage.objects[(original.bucket, result.processed_object_key)] == b"processed"


def test_remove_background_route_exists() -> None:
    from app.api.v1 import background_routes
    from app.main import app

    class FakeBackgroundRemovalService:
        def remove_background(
            self, image_id: str, processed_prefix: str
        ) -> BackgroundRemovalResponse:
            assert image_id == "att_1"
            assert processed_prefix == "ai-fashion/clothes/processed/"
            return BackgroundRemovalResponse(
                image_id=image_id,
                original_object_key="ai-fashion/clothes/raw/att_1.png",
                processed_object_key="ai-fashion/clothes/processed/att_2_nobg.png",
                status="BACKGROUND_REMOVED",
            )

    app.dependency_overrides[background_routes.get_background_removal_service] = (
        FakeBackgroundRemovalService
    )
    try:
        response = TestClient(app).post("/api/v1/background/remove", json={"image_id": "att_1"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "image_id": "att_1",
            "original_object_key": "ai-fashion/clothes/raw/att_1.png",
            "processed_object_key": "ai-fashion/clothes/processed/att_2_nobg.png",
            "status": "BACKGROUND_REMOVED",
        },
        "message": "OK",
        "stackTrace": None,
        "exceptionCode": None,
    }


def test_remove_background_route_returns_404_for_missing_image() -> None:
    from app.api.v1 import background_routes
    from app.main import app
    from app.modules.background_removal.service import BackgroundRemovalError

    class FakeBackgroundRemovalService:
        def remove_background(
            self,
            image_id: str,
            processed_prefix: str,
        ) -> BackgroundRemovalResponse:
            raise BackgroundRemovalError("NOT_FOUND")

    app.dependency_overrides[background_routes.get_background_removal_service] = (
        FakeBackgroundRemovalService
    )
    try:
        response = TestClient(app).post("/api/v1/background/remove", json={"image_id": "missing"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404


def test_remove_background_route_returns_500_for_processing_error() -> None:
    from app.api.v1 import background_routes
    from app.main import app
    from app.modules.background_removal.service import BackgroundRemovalError

    class FakeBackgroundRemovalService:
        def remove_background(
            self,
            image_id: str,
            processed_prefix: str,
        ) -> BackgroundRemovalResponse:
            raise BackgroundRemovalError("PROCESSING_FAILED")

    app.dependency_overrides[background_routes.get_background_removal_service] = (
        FakeBackgroundRemovalService
    )
    try:
        response = TestClient(app).post("/api/v1/background/remove", json={"image_id": "att_1"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500
