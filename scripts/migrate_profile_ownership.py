from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = ROOT_DIR / "backend" / "storage" / "eduagent.sqlite3"

PROFILE_OWNERS: dict[tuple[str, str], tuple[str, str]] = {
    ("李明", "Python 程序设计"): ("student_001", "demo-basic"),
    ("张三", "Python 爬虫基础与实践"): ("demo_student_zhangsan", "demo-zhangsan"),
    ("李四", "Python 爬虫基础与实践"): ("demo_student_lisi", "demo-lisi"),
    ("王五", "数据结构与算法"): ("demo_student_wangwu", "demo-wangwu"),
    ("张三", "Web 开发技术"): ("demo_student_zhangsan", "demo-zhangsan"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    return {str(row[1]) for row in connection.execute(f"PRAGMA table_info({table_name})")}


def load_profile_rows(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    columns = table_columns(connection, "student_profiles")
    owner_expr = "p.owner_user_id" if "owner_user_id" in columns else "NULL"
    key_expr = "p.demo_profile_key" if "demo_profile_key" in columns else "NULL"
    return connection.execute(
        f"""
        SELECT
            p.id,
            p.student_name,
            p.course_id,
            c.title AS course_title,
            p.profile_json,
            {owner_expr} AS owner_user_id,
            {key_expr} AS demo_profile_key
        FROM student_profiles AS p
        JOIN courses AS c ON c.id = p.course_id
        ORDER BY p.id
        """
    ).fetchall()


def build_plan(connection: sqlite3.Connection) -> dict[str, Any]:
    rows = load_profile_rows(connection)
    changes: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []

    for row in rows:
        mapping = PROFILE_OWNERS.get((row["student_name"], row["course_title"]))
        if not mapping:
            conflicts.append(
                {
                    "profile_id": row["id"],
                    "student_name": row["student_name"],
                    "course_title": row["course_title"],
                    "reason": "没有唯一的显式所有者映射",
                }
            )
            continue

        target_owner, target_key = mapping
        current_owner = str(row["owner_user_id"] or "").strip()
        current_key = str(row["demo_profile_key"] or "").strip()
        if current_owner and current_owner != target_owner:
            conflicts.append(
                {
                    "profile_id": row["id"],
                    "student_name": row["student_name"],
                    "course_title": row["course_title"],
                    "reason": "现有所有者与显式映射冲突",
                    "current_owner": current_owner,
                    "expected_owner": target_owner,
                }
            )
            continue

        try:
            raw = json.loads(row["profile_json"] or "{}")
        except json.JSONDecodeError:
            conflicts.append(
                {
                    "profile_id": row["id"],
                    "student_name": row["student_name"],
                    "course_title": row["course_title"],
                    "reason": "profile_json 无法解析",
                }
            )
            continue
        if not isinstance(raw, dict):
            conflicts.append(
                {
                    "profile_id": row["id"],
                    "student_name": row["student_name"],
                    "course_title": row["course_title"],
                    "reason": "profile_json 不是对象",
                }
            )
            continue

        if (
            target_owner == "demo_student_zhangsan"
            and row["course_title"] == "Web 开发技术"
            and (
                current_key == "demo-zhangsan-legacy"
                or bool(raw.get("legacy_user_id"))
                or str(raw.get("user_id") or "").strip()
                not in {"", "demo_student_zhangsan"}
            )
        ):
            target_key = "demo-zhangsan-legacy"

        legacy_user_id = raw.get("user_id")
        desired_identity = {
            "user_id": target_owner,
            "student_name": row["student_name"],
            "display_name": row["student_name"],
            "course_id": row["course_id"],
        }
        json_needs_update = any(raw.get(key) != value for key, value in desired_identity.items())
        if current_owner != target_owner or current_key != target_key or json_needs_update:
            changes.append(
                {
                    "profile_id": row["id"],
                    "student_name": row["student_name"],
                    "course_title": row["course_title"],
                    "from_owner": current_owner or None,
                    "to_owner": target_owner,
                    "from_demo_profile_key": current_key or None,
                    "to_demo_profile_key": target_key,
                    "legacy_user_id": legacy_user_id,
                }
            )

    return {
        "profile_count": len(rows),
        "change_count": len(changes),
        "conflict_count": len(conflicts),
        "changes": changes,
        "conflicts": conflicts,
    }


def apply_migration(database: Path, backup_dir: Path) -> dict[str, Any]:
    database = database.resolve()
    backup_dir = backup_dir.resolve()
    backup_dir.mkdir(parents=True, exist_ok=True)

    before_hash = sha256(database)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"{database.stem}_migration_backup_{stamp}{database.suffix}"
    if backup.exists():
        raise RuntimeError(f"备份文件已存在：{backup}")
    shutil.copy2(database, backup)
    backup_hash = sha256(backup)
    if backup_hash != before_hash:
        raise RuntimeError("迁移前数据库备份哈希不一致")

    connection = sqlite3.connect(str(database))
    connection.row_factory = sqlite3.Row
    try:
        plan = build_plan(connection)
        if plan["conflict_count"]:
            raise RuntimeError("存在无法唯一处理的画像所有者冲突")

        before_count = int(connection.execute("SELECT COUNT(*) FROM student_profiles").fetchone()[0])
        connection.execute("BEGIN IMMEDIATE")
        columns = table_columns(connection, "student_profiles")
        if "owner_user_id" not in columns:
            connection.execute("ALTER TABLE student_profiles ADD COLUMN owner_user_id VARCHAR(100)")
        if "demo_profile_key" not in columns:
            connection.execute("ALTER TABLE student_profiles ADD COLUMN demo_profile_key VARCHAR(100)")
        connection.execute(
            "CREATE INDEX IF NOT EXISTS ix_student_profiles_owner_user_id "
            "ON student_profiles (owner_user_id)"
        )

        for change in plan["changes"]:
            row = connection.execute(
                """
                SELECT p.id, p.student_name, p.course_id, c.title AS course_title, p.profile_json
                FROM student_profiles AS p
                JOIN courses AS c ON c.id = p.course_id
                WHERE p.id = ?
                """,
                (change["profile_id"],),
            ).fetchone()
            if row is None:
                raise RuntimeError(f"画像在迁移期间消失：{change['profile_id']}")
            raw = json.loads(row["profile_json"] or "{}")
            old_user_id = raw.get("user_id")
            if old_user_id and old_user_id != change["to_owner"]:
                raw["legacy_user_id"] = old_user_id
            raw.update(
                {
                    "user_id": change["to_owner"],
                    "student_name": row["student_name"],
                    "display_name": row["student_name"],
                    "course_id": row["course_id"],
                    "course_name": row["course_title"],
                }
            )
            connection.execute(
                """
                UPDATE student_profiles
                SET owner_user_id = ?, demo_profile_key = ?, profile_json = ?
                WHERE id = ?
                """,
                (
                    change["to_owner"],
                    change["to_demo_profile_key"],
                    json.dumps(raw, ensure_ascii=False),
                    change["profile_id"],
                ),
            )

        missing_owners = int(
            connection.execute(
                "SELECT COUNT(*) FROM student_profiles "
                "WHERE owner_user_id IS NULL OR TRIM(owner_user_id) = ''"
            ).fetchone()[0]
        )
        after_count = int(connection.execute("SELECT COUNT(*) FROM student_profiles").fetchone()[0])
        if missing_owners:
            raise RuntimeError(f"迁移后仍有 {missing_owners} 条画像缺少所有者")
        if before_count != after_count:
            raise RuntimeError("迁移前后画像数量不一致")
        integrity = str(connection.execute("PRAGMA integrity_check").fetchone()[0])
        if integrity.lower() != "ok":
            raise RuntimeError(f"SQLite 完整性检查失败：{integrity}")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    after_hash = sha256(database)
    return {
        **plan,
        "status": "migrated",
        "database": str(database),
        "backup": str(backup),
        "before_sha256": before_hash,
        "backup_sha256": backup_hash,
        "after_sha256": after_hash,
        "integrity_check": "ok",
    }


def dry_run(database: Path) -> dict[str, Any]:
    database = database.resolve()
    connection = sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        plan = build_plan(connection)
        integrity = str(connection.execute("PRAGMA integrity_check").fetchone()[0])
    finally:
        connection.close()
    return {
        **plan,
        "status": "dry-run",
        "database": str(database),
        "database_sha256": sha256(database),
        "integrity_check": integrity,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="为学生画像迁移稳定所有者标识。")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--backup-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    database = args.database.resolve()
    if not database.is_file():
        print(json.dumps({"status": "error", "message": "数据库文件不存在"}, ensure_ascii=False))
        return 2
    try:
        if args.dry_run:
            result = dry_run(database)
        else:
            if args.backup_dir is None:
                raise RuntimeError("正式迁移必须提供 --backup-dir")
            result = apply_migration(database, args.backup_dir)
    except Exception as exc:
        print(
            json.dumps(
                {"status": "error", "message": str(exc), "database": str(database)},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not result.get("conflict_count") else 2


if __name__ == "__main__":
    sys.exit(main())
