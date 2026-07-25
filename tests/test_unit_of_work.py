from __future__ import annotations

from collections.abc import Callable, Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.database.models import Base
from app.infrastructure.database.unit_of_work import UnitOfWork

SessionFactory = Callable[[], Session]


@pytest.fixture()
def session_factory() -> Iterator[SessionFactory]:
    # One shared in-memory database across every connection this factory hands
    # out, so a second UnitOfWork can observe what a previous one committed.
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    maker = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    yield maker


def _create_attachment(uow: UnitOfWork, attachment_id: str) -> None:
    uow.attachments.create(
        id=attachment_id,
        object_key=f"raw/{attachment_id}.png",
        bucket="style-engine",
        original_filename=f"{attachment_id}.png",
        content_type="image/png",
        size=123,
        status="UPLOADED",
        is_deleted=False,
        source_attachment_id=None,
    )


def test_commit_persists(session_factory: SessionFactory) -> None:
    with UnitOfWork(session_factory=session_factory) as uow:
        _create_attachment(uow, "att_1")
        uow.commit()

    with UnitOfWork(session_factory=session_factory) as verify:
        assert verify.attachments.get_active_by_id("att_1") is not None


def test_without_commit_nothing_persists(session_factory: SessionFactory) -> None:
    with UnitOfWork(session_factory=session_factory) as uow:
        _create_attachment(uow, "att_2")
        # Intentionally no commit.

    with UnitOfWork(session_factory=session_factory) as verify:
        assert verify.attachments.get_active_by_id("att_2") is None


def test_rollback_on_error_persists_nothing(session_factory: SessionFactory) -> None:
    with pytest.raises(RuntimeError):
        with UnitOfWork(session_factory=session_factory) as uow:
            _create_attachment(uow, "att_3")
            raise RuntimeError("boom before commit")

    with UnitOfWork(session_factory=session_factory) as verify:
        assert verify.attachments.get_active_by_id("att_3") is None
