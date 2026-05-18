from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings


def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(settings.database_url, future=True)


SessionLocal = sessionmaker[Session](
    autocommit=False,
    autoflush=False,
    bind=get_engine(),
    future=True,
)
