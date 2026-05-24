from collections.abc import Generator

import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import settings


if settings.resolved_database_url.startswith("sqlite"):
    sqlite_path = settings.path_from_root(settings.sqlite_fallback_path)
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        "sqlite://",
        pool_pre_ping=True,
        creator=lambda: sqlite3.connect(str(sqlite_path), check_same_thread=False),
    )
else:
    engine = create_engine(settings.resolved_database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
