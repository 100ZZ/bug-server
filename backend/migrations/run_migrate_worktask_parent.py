#!/usr/bin/env python3
"""执行 work_tasks.parent_id 迁移（本地开发用，与 Docker 03 脚本同源、幂等）
在 backend 目录执行: python migrations/run_migrate_worktask_parent.py
"""
import sys
from pathlib import Path

from sqlalchemy import text

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from config import engine  # noqa: E402


def _statements(sql: str) -> list[str]:
    lines = []
    for line in sql.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        lines.append(line)
    joined = "\n".join(lines)
    out: list[str] = []
    for part in joined.split(";"):
        p = part.strip()
        if p:
            out.append(p)
    return out


def main():
    sql_path = Path(__file__).resolve().parent / "migrate_add_worktask_parent.sql"
    if not sql_path.is_file():
        print(f"❌ 未找到迁移文件: {sql_path}")
        sys.exit(1)
    sql_text = sql_path.read_text(encoding="utf-8")
    try:
        with engine.begin() as conn:
            for stmt in _statements(sql_text):
                conn.execute(text(stmt))
        print("✅ 迁移已执行：work_tasks.parent_id（若已存在则已跳过）")
    except Exception as e:
        if "Duplicate column name 'parent_id'" in str(e) or "already exists" in str(e).lower():
            print("ℹ️ parent_id 已存在，无需重复迁移")
            sys.exit(0)
        print(f"❌ 迁移失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
