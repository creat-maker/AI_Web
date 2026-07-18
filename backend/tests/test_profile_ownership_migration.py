from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from scripts.migrate_profile_ownership import apply_migration, dry_run


def _create_legacy_database(path: Path, *, student_name: str = "李明") -> None:
    connection = sqlite3.connect(path)
    try:
        connection.executescript(
            """
            CREATE TABLE courses (
                id INTEGER PRIMARY KEY,
                title VARCHAR(200) NOT NULL
            );
            CREATE TABLE student_profiles (
                id INTEGER PRIMARY KEY,
                student_name VARCHAR(100) NOT NULL,
                course_id INTEGER NOT NULL,
                profile_json TEXT
            );
            INSERT INTO courses (id, title) VALUES (1, 'Python 程序设计');
            """
        )
        connection.execute(
            """
            INSERT INTO student_profiles (id, student_name, course_id, profile_json)
            VALUES (1, ?, 1, ?)
            """,
            (student_name, '{"user_id": "demo-basic"}'),
        )
        connection.commit()
    finally:
        connection.close()


def test_migration_is_backed_up_and_idempotent(tmp_path: Path):
    database = tmp_path / "legacy.sqlite3"
    backup_dir = tmp_path / "backups"
    _create_legacy_database(database)

    before = dry_run(database)
    assert before["change_count"] == 1
    assert before["conflict_count"] == 0

    result = apply_migration(database, backup_dir)
    assert result["status"] == "migrated"
    assert result["before_sha256"] == result["backup_sha256"]
    assert Path(result["backup"]).is_file()

    connection = sqlite3.connect(database)
    try:
        row = connection.execute(
            "SELECT owner_user_id, demo_profile_key, profile_json FROM student_profiles WHERE id = 1"
        ).fetchone()
        assert row is not None
        assert row[0] == "student_001"
        assert row[1] == "demo-basic"
        assert '"user_id": "student_001"' in row[2]
    finally:
        connection.close()

    after = dry_run(database)
    assert after["change_count"] == 0
    assert after["conflict_count"] == 0


def test_migration_conflict_does_not_change_database(tmp_path: Path):
    database = tmp_path / "conflict.sqlite3"
    backup_dir = tmp_path / "backups"
    _create_legacy_database(database, student_name="未知学生")

    before = dry_run(database)
    assert before["conflict_count"] == 1

    with pytest.raises(RuntimeError, match="冲突"):
        apply_migration(database, backup_dir)

    connection = sqlite3.connect(database)
    try:
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(student_profiles)").fetchall()
        }
        assert "owner_user_id" not in columns
        assert connection.execute("SELECT COUNT(*) FROM student_profiles").fetchone()[0] == 1
    finally:
        connection.close()


def test_current_zhangsan_profile_is_not_reclassified_as_legacy(tmp_path: Path):
    database = tmp_path / "current.sqlite3"
    connection = sqlite3.connect(database)
    try:
        connection.executescript(
            """
            CREATE TABLE courses (
                id INTEGER PRIMARY KEY,
                title VARCHAR(200) NOT NULL
            );
            CREATE TABLE student_profiles (
                id INTEGER PRIMARY KEY,
                student_name VARCHAR(100) NOT NULL,
                course_id INTEGER NOT NULL,
                profile_json TEXT,
                owner_user_id VARCHAR(100),
                demo_profile_key VARCHAR(100)
            );
            INSERT INTO courses (id, title) VALUES (1, 'Web 开发技术');
            INSERT INTO student_profiles (
                id,
                student_name,
                course_id,
                profile_json,
                owner_user_id,
                demo_profile_key
            ) VALUES (
                1,
                '张三',
                1,
                '{"user_id": "demo_student_zhangsan", "student_name": "张三", "display_name": "张三", "course_id": 1}',
                'demo_student_zhangsan',
                'demo-zhangsan'
            );
            """
        )
        connection.commit()
    finally:
        connection.close()

    result = dry_run(database)
    assert result["change_count"] == 0
    assert result["conflict_count"] == 0
