from __future__ import annotations

from importlib import import_module
from pathlib import Path

import pytest
from sqlalchemy import Column, Index, MetaData, String, Table, create_engine
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


def test_migration_placeholder(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    db_path = tmp_path / "migration.db"
    db_url = f"sqlite+pysqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", db_url)

    from app.config.settings import get_settings

    get_settings.cache_clear()

    engine = create_engine(db_url, future=True)
    metadata = MetaData()
    attachments = Table(
        "attachments",
        metadata,
        Column("id", String, primary_key=True),
        Column("source_attachment_id", String, nullable=True),
    )
    Index("ix_attachments_source_attachment_id", attachments.c.source_attachment_id)
    metadata.create_all(engine)

    migration = import_module("app.infrastructure.database.migrations.2026_05_18_add_source_attachment_id")

    monkeypatch.setattr(
        type(attachments.c.source_attachment_id),
        "drop",
        lambda self, *args, **kwargs: None,
        raising=False,
    )

    captured = {"called": False, "checkfirst": None}
    original_drop = Index.drop

    def drop(self: Index, bind=None, checkfirst: bool | None = None):
        captured["called"] = True
        captured["checkfirst"] = checkfirst
        return original_drop(self, bind=bind, checkfirst=checkfirst)

    monkeypatch.setattr(Index, "drop", drop, raising=True)

    migration.downgrade()

    assert captured["called"] is True
    assert captured["checkfirst"] is True
