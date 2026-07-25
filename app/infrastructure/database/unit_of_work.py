from __future__ import annotations

from collections.abc import Callable
from types import TracebackType

from sqlalchemy.orm import Session

from app.infrastructure.database.attachments_repo import AttachmentRepository
from app.infrastructure.database.session import create_session


class UnitOfWork:
    """Single transaction boundary for a business operation.

    Owns the session and the repositories bound to it. Callers do their work
    through the repositories and call `commit()` exactly once; on an exception
    the block rolls back. Repositories never commit themselves, so a multi-step
    operation is all-or-nothing.

    Usage::

        with UnitOfWork() as uow:
            uow.attachments.create(...)
            uow.attachments.update_status(...)
            uow.commit()
    """

    session: Session
    attachments: AttachmentRepository

    def __init__(self, session_factory: Callable[[], Session] = create_session) -> None:
        self._session_factory = session_factory

    def __enter__(self) -> UnitOfWork:
        self.session = self._session_factory()
        self.attachments = AttachmentRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        try:
            if exc_type is not None:
                self.rollback()
        finally:
            self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
