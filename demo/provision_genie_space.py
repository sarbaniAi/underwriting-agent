#!/usr/bin/env python3
"""Create Genie space for India underwriting demo tables.

Reads from environment: DATABRICKS_CONFIG_PROFILE, DATABRICKS_SQL_WAREHOUSE_ID,
UC_CATALOG, UC_SCHEMA.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

PROFILE = os.environ.get("DATABRICKS_CONFIG_PROFILE", "DEFAULT")
WAREHOUSE_ID = os.environ.get("DATABRICKS_SQL_WAREHOUSE_ID", "")
CATALOG = os.environ.get("UC_CATALOG", "")
SCHEMA = os.environ.get("UC_SCHEMA", "")
BASE = f"{CATALOG}.{SCHEMA}"


def nid() -> str:
    return uuid.uuid4().hex


def build_serialized_space() -> str:
    space = {
        "version": 2,
        "config": {
            "sample_questions": sorted([
                {"id": nid(), "question": ["How many applications were declined?"]},
                {"id": nid(), "question": ["What is the maximum sum assured in INR for product PRD-TERM-001?"]},
                {"id": nid(), "question": ["List approved underwriting decisions with sum assured"]},
            ], key=lambda x: x["id"])
        },
        "data_sources": {
            "tables": sorted([
                {"identifier": f"{BASE}.dim_applicant", "description": ["Synthetic applicant demographics; no real PII."]},
                {"identifier": f"{BASE}.dim_product", "description": ["Synthetic India insurance products (demo)."]},
                {"identifier": f"{BASE}.fact_application", "description": ["Policy applications and workflow status."]},
                {"identifier": f"{BASE}.fact_underwriting_decision", "description": ["Final outcomes: approved, declined, postponed."]},
                {"identifier": f"{BASE}.ref_reason_code", "description": ["Decline and postpone reason codes."]},
                {"identifier": f"{BASE}.ref_underwriting_limits", "description": ["Max sum assured (INR) and age bands by product."]},
            ], key=lambda t: t["identifier"]),
            "metric_views": [],
        },
        "instructions": {
            "text_instructions": sorted([{
                "id": nid(),
                "content": [
                    f"India retail life underwriting demo. All data is synthetic. "
                    f"Use INR for monetary amounts. Join fact_application to dim_applicant on applicant_id, "
                    f"to dim_product on product_id, and fact_underwriting_decision to fact_application on application_id."
                ],
            }], key=lambda x: x["id"]),
            "example_question_sqls": [],
            "sql_functions": sorted([
                {"id": nid(), "identifier": f"{BASE}.fn_max_sum_assured_inr"},
                {"id": nid(), "identifier": f"{BASE}.fn_risk_tier"},
                {"id": nid(), "identifier": f"{BASE}.fn_ulip_smoker_blocked"},
            ], key=lambda x: x["id"]),
            "join_specs": [],
            "sql_snippets": {"filters": [], "expressions": [], "measures": []},
        },
        "benchmarks": {"questions": []},
    }
    return json.dumps(space, separators=(",", ":"))


def main() -> None:
    if not WAREHOUSE_ID or not CATALOG or not SCHEMA:
        print("ERROR: Set DATABRICKS_SQL_WAREHOUSE_ID, UC_CATALOG, UC_SCHEMA", file=sys.stderr)
        sys.exit(1)

    payload = {
        "warehouse_id": WAREHOUSE_ID,
        "title": "India Underwriter (demo)",
        "description": "Synthetic underwriting warehouse tables for multi-agent demo",
        "serialized_space": build_serialized_space(),
    }
    proc = subprocess.run(
        ["databricks", "api", "post", "/api/2.0/genie/spaces",
         "--json", json.dumps(payload), "-o", "json"],
        cwd="/tmp",
        env={**os.environ, "DATABRICKS_CONFIG_PROFILE": PROFILE},
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        sys.exit(1)
    out = json.loads(proc.stdout)
    space_id = out.get("space_id")
    print(json.dumps(out, indent=2))
    if space_id:
        p = Path(__file__).resolve().parent / "genie_space_id.txt"
        p.write_text(space_id + "\n", encoding="utf-8")
        print(f"\nGenie space_id: {space_id}", file=sys.stderr)
        print(f"Written to {p}", file=sys.stderr)
        print(f"\nUpdate GENIE_SPACE_ID in your .env file with this value.", file=sys.stderr)


if __name__ == "__main__":
    main()
