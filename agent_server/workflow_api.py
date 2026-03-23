"""
Workflow API endpoints for the underwriting workspace.
Provides CRUD for applications, AI analysis, and analyst adjustments.
"""

import os
import json
from datetime import datetime
from uuid import uuid4
from typing import Optional

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import Disposition, StatementState
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api")

CATALOG = os.environ.get("UC_CATALOG", "serverless_stable_tcrn2v_catalog")
SCHEMA = os.environ.get("UC_SCHEMA", "underwriting_demo")
WAREHOUSE_ID = os.environ.get("DATABRICKS_WAREHOUSE_ID", "91dbe14a27ddabad")

_ws = WorkspaceClient()


def _exec(sql: str) -> list[dict]:
    resp = _ws.statement_execution.execute_statement(
        warehouse_id=WAREHOUSE_ID, statement=sql, wait_timeout="30s", disposition=Disposition.INLINE,
    )
    if resp.status.state != StatementState.SUCCEEDED:
        msg = resp.status.error.message if resp.status.error else "Query failed"
        raise HTTPException(status_code=500, detail=msg)
    if not resp.result or not resp.result.data_array:
        return []
    cols = [c.name for c in resp.manifest.schema.columns]
    return [dict(zip(cols, row)) for row in resp.result.data_array]


def _esc(v: str) -> str:
    if v is None:
        return "NULL"
    return v.replace("\\", "\\\\").replace("'", "\\'")


# ── List applicants (for dropdown) ──────────────────────────────────────────

@router.get("/applicants")
def list_applicants():
    rows = _exec(f"""
        SELECT DISTINCT a.applicant_id, a.gender, a.birth_year, a.smoker_status, a.bmi_bucket,
               a.state_ut, a.occupation_class
        FROM {CATALOG}.{SCHEMA}.dim_applicant a
        JOIN {CATALOG}.{SCHEMA}.fact_application f ON a.applicant_id = f.applicant_id
        ORDER BY a.applicant_id
    """)
    return {"applicants": rows}


# ── Get full application detail ─────────────────────────────────────────────

@router.get("/application/{application_id}")
def get_application(application_id: str):
    rows = _exec(f"""
        SELECT a.applicant_id, a.gender, a.birth_year, a.smoker_status, a.bmi_bucket,
               a.state_ut, a.occupation_class,
               f.application_id, f.product_id, f.application_date, f.status, f.channel,
               p.product_name, p.product_line,
               d.decision_id, d.decision_date, d.outcome, d.reason_code,
               d.sum_assured_inr, d.approved_risk_class,
               r.description AS reason_description, r.category AS reason_category,
               l.max_sum_assured_inr AS product_max_sa, l.age_min, l.age_max, l.smoker_allowed
        FROM {CATALOG}.{SCHEMA}.fact_application f
        JOIN {CATALOG}.{SCHEMA}.dim_applicant a ON a.applicant_id = f.applicant_id
        JOIN {CATALOG}.{SCHEMA}.dim_product p ON p.product_id = f.product_id
        LEFT JOIN {CATALOG}.{SCHEMA}.fact_underwriting_decision d ON d.application_id = f.application_id
        LEFT JOIN {CATALOG}.{SCHEMA}.ref_reason_code r ON r.reason_code = d.reason_code
        LEFT JOIN {CATALOG}.{SCHEMA}.ref_underwriting_limits l ON l.product_id = f.product_id
        WHERE f.application_id = '{_esc(application_id)}'
    """)
    if not rows:
        raise HTTPException(status_code=404, detail="Application not found")
    return rows[0]


# ── List applications for an applicant ──────────────────────────────────────

@router.get("/applicant/{applicant_id}/applications")
def list_applications(applicant_id: str):
    rows = _exec(f"""
        SELECT f.application_id, f.product_id, f.application_date, f.status, f.channel,
               p.product_name, p.product_line,
               d.outcome, d.sum_assured_inr, d.approved_risk_class
        FROM {CATALOG}.{SCHEMA}.fact_application f
        JOIN {CATALOG}.{SCHEMA}.dim_product p ON p.product_id = f.product_id
        LEFT JOIN {CATALOG}.{SCHEMA}.fact_underwriting_decision d ON d.application_id = f.application_id
        WHERE f.applicant_id = '{_esc(applicant_id)}'
        ORDER BY f.application_date DESC
    """)
    return {"applications": rows}


# ── Workspace: save analyst adjustment ──────────────────────────────────────

class WorkspaceEntry(BaseModel):
    application_id: str
    analyst_name: Optional[str] = "demo_analyst"
    risk_class_override: Optional[str] = None
    substandard_rating: Optional[float] = None
    coverage_approved_inr: Optional[int] = None
    ai_recommendation: Optional[str] = None
    analyst_notes: Optional[str] = None
    status: Optional[str] = "pending"


@router.post("/workspace")
def save_workspace(entry: WorkspaceEntry):
    wid = str(uuid4())[:8]
    now = datetime.utcnow().isoformat()

    # 1. Insert into workspace audit table
    _exec(f"""
        INSERT INTO {CATALOG}.{SCHEMA}.underwriter_workspace
        (workspace_id, application_id, analyst_name, risk_class_override,
         substandard_rating, coverage_approved_inr, ai_recommendation,
         analyst_notes, status, created_at, updated_at)
        VALUES ('{wid}', '{_esc(entry.application_id)}', '{_esc(entry.analyst_name)}',
                '{_esc(entry.risk_class_override)}', {entry.substandard_rating or 'NULL'},
                {entry.coverage_approved_inr or 'NULL'},
                '{_esc(entry.ai_recommendation)}', '{_esc(entry.analyst_notes)}',
                '{_esc(entry.status)}', '{now}', '{now}')
    """)

    # 2. Update fact_underwriting_decision if this is a final decision
    final_statuses = ("approved", "declined", "approved_with_changes")
    if entry.status in final_statuses:
        outcome = "approved" if entry.status in ("approved", "approved_with_changes") else "declined"
        risk_class = entry.risk_class_override or "standard"
        sa = entry.coverage_approved_inr or 0

        # Extract reason code from notes if declined (format: [DECLINE: reason_text] ...)
        reason_code = "NULL"
        if entry.status == "declined" and entry.analyst_notes:
            import re
            m = re.search(r'\[DECLINE:\s*(.+?)\]', entry.analyst_notes)
            if m:
                # Try to match to a reason code by searching ref_reason_code
                reason_text = m.group(1).strip()
                codes = _exec(f"""
                    SELECT reason_code FROM {CATALOG}.{SCHEMA}.ref_reason_code
                    WHERE description LIKE '%{_esc(reason_text[:30])}%' LIMIT 1
                """)
                if codes:
                    reason_code = f"'{codes[0]['reason_code']}'"

        # MERGE into fact_underwriting_decision
        _exec(f"""
            MERGE INTO {CATALOG}.{SCHEMA}.fact_underwriting_decision AS t
            USING (SELECT '{_esc(entry.application_id)}' AS application_id) AS s
            ON t.application_id = s.application_id
            WHEN MATCHED THEN UPDATE SET
                outcome = '{outcome}',
                approved_risk_class = '{_esc(risk_class)}',
                sum_assured_inr = {sa},
                reason_code = {reason_code},
                decision_date = '{now[:10]}'
            WHEN NOT MATCHED THEN INSERT
                (decision_id, application_id, decision_date, outcome, reason_code,
                 sum_assured_inr, approved_risk_class)
            VALUES ('DEC-{wid}', '{_esc(entry.application_id)}', '{now[:10]}',
                    '{outcome}', {reason_code}, {sa}, '{_esc(risk_class)}')
        """)

        # Also update fact_application status
        app_status = "approved" if outcome == "approved" else "declined"
        _exec(f"""
            UPDATE {CATALOG}.{SCHEMA}.fact_application
            SET status = '{app_status}'
            WHERE application_id = '{_esc(entry.application_id)}'
        """)

    # 3. Update fact_application to 'in_review' for info_requested
    if entry.status == "info_requested":
        _exec(f"""
            UPDATE {CATALOG}.{SCHEMA}.fact_application
            SET status = 'in_review'
            WHERE application_id = '{_esc(entry.application_id)}'
        """)

    return {"workspace_id": wid, "status": "saved", "decision": entry.status}


@router.get("/workspace/{application_id}")
def get_workspace(application_id: str):
    rows = _exec(f"""
        SELECT * FROM {CATALOG}.{SCHEMA}.underwriter_workspace
        WHERE application_id = '{_esc(application_id)}'
        ORDER BY updated_at DESC LIMIT 1
    """)
    return rows[0] if rows else {}


# ── Decision history for an application ─────────────────────────────────────

@router.get("/workspace/{application_id}/history")
def get_workspace_history(application_id: str):
    rows = _exec(f"""
        SELECT workspace_id, analyst_name, status, risk_class_override,
               substandard_rating, coverage_approved_inr, analyst_notes,
               created_at
        FROM {CATALOG}.{SCHEMA}.underwriter_workspace
        WHERE application_id = '{_esc(application_id)}'
        ORDER BY created_at DESC
        LIMIT 20
    """)
    return {"history": rows}
