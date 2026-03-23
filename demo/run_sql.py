#!/usr/bin/env python3
"""Execute SQL statements against a Databricks SQL warehouse.

Reads DATABRICKS_CONFIG_PROFILE and DATABRICKS_SQL_WAREHOUSE_ID from environment.
All catalog/schema references inside the SQL files use a placeholder that is
replaced at runtime with the values from UC_CATALOG and UC_SCHEMA env vars.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

PROFILE = os.environ.get("DATABRICKS_CONFIG_PROFILE", "DEFAULT")
WAREHOUSE_ID = os.environ.get("DATABRICKS_SQL_WAREHOUSE_ID", "")
CATALOG = os.environ.get("UC_CATALOG", "")
SCHEMA = os.environ.get("UC_SCHEMA", "")

if not WAREHOUSE_ID:
    print("ERROR: Set DATABRICKS_SQL_WAREHOUSE_ID in your .env or environment", file=sys.stderr)
    sys.exit(1)
if not CATALOG or not SCHEMA:
    print("ERROR: Set UC_CATALOG and UC_SCHEMA in your .env or environment", file=sys.stderr)
    sys.exit(1)


def run_sql(statement: str) -> dict:
    statement = statement.strip()
    if not statement or statement.startswith("--"):
        return {}
    # Replace catalog.schema placeholder
    statement = statement.replace("__CATALOG__.__SCHEMA__", f"{CATALOG}.{SCHEMA}")
    body = {
        "warehouse_id": WAREHOUSE_ID,
        "statement": statement,
        "wait_timeout": "50s",
        "on_wait_timeout": "CONTINUE",
    }
    proc = subprocess.run(
        ["databricks", "api", "post", "/api/2.0/sql/statements",
         "--json", json.dumps(body), "-o", "json"],
        cwd="/tmp",
        env={**os.environ, "DATABRICKS_CONFIG_PROFILE": PROFILE},
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout)
    out = json.loads(proc.stdout)
    st = out.get("status", {})
    if st.get("state") == "FAILED":
        err = st.get("error", {})
        raise RuntimeError(err.get("message", json.dumps(out)))
    return out


def main() -> None:
    sql_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "setup_underwriting_demo.sql"
    raw = sql_path.read_text(encoding="utf-8")
    parts, buf = [], []
    for line in raw.splitlines():
        stripped = line.strip()
        if not buf and (not stripped or stripped.startswith("--")):
            continue
        buf.append(line)
        if line.rstrip().endswith(";"):
            parts.append("\n".join(buf))
            buf = []
    if buf:
        parts.append("\n".join(buf))
    for i, stmt in enumerate(parts):
        stmt = stmt.strip().rstrip(";").strip()
        if not stmt:
            continue
        print(f"-- [{i + 1}/{len(parts)}] {stmt[:72]}...", file=sys.stderr)
        run_sql(stmt + ";")
    print("OK", file=sys.stderr)


if __name__ == "__main__":
    main()
