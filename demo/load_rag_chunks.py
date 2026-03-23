#!/usr/bin/env python3
"""Insert knowledge_docs markdown into rag_chunks (run after provision_stack.sql)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from run_sql import run_sql  # noqa: E402

CATALOG = os.environ.get("UC_CATALOG", "")
SCHEMA = os.environ.get("UC_SCHEMA", "")


def main() -> None:
    if not CATALOG or not SCHEMA:
        print("ERROR: Set UC_CATALOG and UC_SCHEMA", file=sys.stderr)
        sys.exit(1)
    run_sql(f"TRUNCATE TABLE {CATALOG}.{SCHEMA}.rag_chunks;")
    kd = _ROOT / "knowledge_docs"
    for p in sorted(kd.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        chunk_id = p.stem.replace("-", "_")[:64]
        fname_esc = p.name.replace("'", "''")
        content_esc = text.replace("'", "''")
        sql = (
            f"INSERT INTO {CATALOG}.{SCHEMA}.rag_chunks "
            f"VALUES ('{chunk_id}', '{fname_esc}', '{content_esc}');"
        )
        print(f"-- insert {p.name} ({len(text)} chars)", file=sys.stderr)
        run_sql(sql)


if __name__ == "__main__":
    main()
