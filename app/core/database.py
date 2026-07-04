from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

connect_args = {}
engine_kwargs = {
    'pool_pre_ping': True,
    'future': True,
}

if settings.database_url.startswith('sqlite'):
    connect_args = {'check_same_thread': False}
else:
    engine_kwargs.update(
        {
            'pool_size': settings.database_pool_size,
            'max_overflow': settings.database_max_overflow,
            'pool_recycle': settings.database_pool_recycle_seconds,
        }
    )

engine = create_engine(settings.database_url, connect_args=connect_args, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
