from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.models import Base


class BaseRepository[ModelT: Base]:
    """Generic CRUD building blocks shared by concrete repositories.

    Deliberately thin: SQLAlchemy's Session already is a repository + unit of
    work, so this only removes boilerplate. It never commits — the transaction
    boundary belongs to the UnitOfWork. `add` flushes so server/Python defaults
    and the primary key are populated within the current transaction.
    """

    model: type[ModelT]

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, entity_id: Any) -> ModelT | None:
        return self.session.get(self.model, entity_id)

    def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        self.session.flush()
        return entity

    def delete(self, entity: ModelT) -> None:
        self.session.delete(entity)

    def list(self) -> Sequence[ModelT]:
        return self.session.execute(select(self.model)).scalars().all()
