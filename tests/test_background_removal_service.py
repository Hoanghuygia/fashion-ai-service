from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.database.attachments_repo import AttachmentRepository
from app.infrastructure.database.models import Base


@pytest.fixture()
def session() -> Session:
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
    assert loaded.is_deleted is False


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

    client = StorageClient.build()

    assert client.bucket == "style-engine-test"
    assert client.client.meta.region_name == "us-west-2"
    assert client.client.meta.endpoint_url == "http://localhost:9000"
    assert client.client.meta.config.s3["addressing_style"] == "path"
