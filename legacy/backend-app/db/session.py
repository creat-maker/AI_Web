import logging
import os
from typing import Generator

import pymysql
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import settings

logger = logging.getLogger("pacer.database")


def _ensure_mysql_database_exists(database_url: str) -> None:
    parsed = make_url(database_url)
    connection = pymysql.connect(
        host=parsed.host or settings.DB_HOST,
        port=parsed.port or settings.DB_PORT,
        user=parsed.username or settings.DB_USER,
        password=parsed.password or settings.DB_PASSWORD,
        charset=parsed.query.get("charset", settings.DB_CHARSET),
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{parsed.database or settings.DB_NAME}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        connection.commit()
    finally:
        connection.close()


def _resolve_database_url() -> str:
    candidate_url = settings.RESOLVED_DATABASE_URI

    try:
        if make_url(candidate_url).drivername.startswith("mysql"):
            _ensure_mysql_database_exists(candidate_url)
        return candidate_url
    except Exception as exc:
        logger.warning("MySQL 不可用，自动回退到 SQLite: %s", exc)
        fallback = settings.get_sqlite_fallback_uri()
        sqlite_parent = os.path.dirname(fallback.replace("sqlite:///", ""))
        if sqlite_parent and not os.path.exists(sqlite_parent):
            os.makedirs(sqlite_parent, exist_ok=True)
        return fallback


RESOLVED_DATABASE_URL = _resolve_database_url()

_engine_options = {
    "pool_pre_ping": settings.ENGINE_POOL_PRE_PING,
    "pool_recycle": settings.ENGINE_POOL_RECYCLE,
}
if RESOLVED_DATABASE_URL.startswith("sqlite"):
    _engine_options["connect_args"] = {"check_same_thread": False}

engine = create_engine(RESOLVED_DATABASE_URL, **_engine_options)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
