# India Underwriting Agent — Multi-Agent Demo on Databricks

A production-ready demonstration of an AI-assisted underwriting workflow for India retail life insurance, built on Databricks using the **OpenAI Agents SDK multi-agent** template from [databricks/app-templates](https://github.com/databricks/app-templates).

## What It Does

An orchestrator agent routes underwriting queries to the right backend:

| Tool | Backend | Use Case |
|------|---------|----------|
| **Genie MCP** | Databricks Genie space | Structured data: applicants, applications, decisions, products, limits |
| **UC Functions** | Unity Catalog SQL functions | Governed rules: max sum assured, risk tier, ULIP smoker block |
| **Vector Search** | RAG over `rag_chunks` index | Policy documents, underwriting manuals, guidelines |

The app includes a **full underwriting workflow UI** with:
- Applicant & application browser
- One-click AI analysis (calls all 3 tools)
- Human decision panel: Approve / Deny / Approve with Changes / Request Information
- Decision audit trail (persisted to Delta table)
- AI chat assistant

---

## Prerequisites (Customer Workspace)

| Requirement | Details |
|-------------|---------|
| **Databricks workspace** | Any cloud (AWS / Azure / GCP) with Unity Catalog enabled |
| **Databricks CLI** | v0.200+ installed locally. [Install guide](https://docs.databricks.com/dev-tools/cli/install.html) |
| **CLI profile** | Authenticated profile. Run: `databricks auth login --host <workspace-url> --profile my-profile` |
| **Catalog + Schema** | A UC catalog and schema you can create tables in. The install script creates all tables. |
| **SQL Warehouse** | A running SQL warehouse (serverless or classic). Note the warehouse ID. |
| **Python 3.11+** | For running install scripts and local dev |
| **uv** (optional) | For local development. [Install](https://docs.astral.sh/uv/getting-started/installation/) |
| **Vector Search** (manual) | A VS endpoint + DELTA_SYNC index over `rag_chunks`. See Step 4 below. |

---

## Quick Start (3 steps)

### Step 1: Configure `.env`

```bash
cp .env.example .env
```

Edit `.env` with your workspace values:

```env
# REQUIRED — change these
DATABRICKS_CONFIG_PROFILE=my-profile      # your CLI profile name
UC_CATALOG=my_catalog                      # your Unity Catalog catalog
UC_SCHEMA=underwriting_demo                # schema name (will be created)
DATABRICKS_SQL_WAREHOUSE_ID=abc123def456   # your SQL warehouse ID

# Set after Step 2 completes
GENIE_SPACE_ID=                            # filled automatically by install
VS_INDEX=my_catalog.underwriting_demo.rag_idx

# Optional — defaults work
ORCHESTRATOR_MODEL=databricks-claude-sonnet-4-5
MLFLOW_EXPERIMENT_ID=                      # filled by install or quickstart
```

### Step 2: Run the install script

```bash
cd demo
bash install.sh
```

This creates:
- 7 Delta tables (products, applicants, applications, decisions, reason codes, limits, workspace)
- 3 UC functions (max sum assured, risk tier, ULIP smoker block)
- RAG chunks table with knowledge docs
- Genie space
- Deploys the Databricks App

### Step 3: Grant permissions + set up Vector Search

```bash
# After the app is deployed, grant its service principal access:
bash demo/grant_permissions.sh
```

**Vector Search** (manual — one-time):
1. Go to **Compute > Vector Search** in your workspace
2. Create endpoint: `underwriter_vs_endpoint` (or your preferred name)
3. Create index:
   - Name: `<catalog>.<schema>.rag_idx`
   - Source table: `<catalog>.<schema>.rag_chunks`
   - Sync mode: **DELTA_SYNC** (triggered)
   - Embedding model: `databricks-gte-large-en`
   - Columns to embed: `content`
   - Metadata columns: `source_path`
4. Update `VS_INDEX` in `.env` if you used a different name
5. Grant the app's service principal `CAN_QUERY` on the VS endpoint

---

## What the Customer Needs to Change

| Item | Where | What to change |
|------|-------|----------------|
| **CLI profile** | `.env` | `DATABRICKS_CONFIG_PROFILE=<your-profile>` |
| **Catalog** | `.env` | `UC_CATALOG=<your-catalog>` |
| **Schema** | `.env` | `UC_SCHEMA=<your-schema>` (default: `underwriting_demo`) |
| **Warehouse ID** | `.env` | `DATABRICKS_SQL_WAREHOUSE_ID=<your-warehouse-id>` |
| **Workspace host** | `databricks.yml` | Under `targets.dev.workspace.host` and `targets.prod.workspace.host` |
| **App name** | `databricks.yml` | Under `resources.apps.underwriting_agent.name` (if you want a different name) |
| **VS endpoint** | `.env` | `VS_ENDPOINT=<your-vs-endpoint-name>` (if different) |
| **VS index** | `.env` | `VS_INDEX=<catalog>.<schema>.rag_idx` |
| **Model** | `.env` | `ORCHESTRATOR_MODEL=<model-name>` (any FMAPI model) |

Everything else works out of the box with the provided synthetic data.

---

## Project Structure

```
underwriting-agent/
├── .env.example                    # <-- COPY TO .env AND CONFIGURE
├── databricks.yml                  # DAB bundle (deploy with: databricks bundle deploy)
├── pyproject.toml                  # Python dependencies
├── README.md                       # This file
│
├── agent_server/                   # Core agent code
│   ├── agent.py                    # Orchestrator: tools, MCP, prompt, @stream/@invoke
│   ├── start_server.py             # FastAPI + workflow UI mount
│   ├── utils.py                    # Auth, streaming helpers
│   ├── workflow_api.py             # REST API: applicants, applications, decisions
│   ├── workflow_ui.py              # Full underwriting workspace HTML
│   └── evaluate_agent.py           # MLflow evaluation
│
├── demo/                           # Data setup scripts
│   ├── install.sh                  # MASTER INSTALL — run this
│   ├── grant_permissions.sh        # Grant app SP permissions
│   ├── setup_underwriting_demo.sql # Tables + seed data
│   ├── provision_stack.sql         # UC functions + rag_chunks table
│   ├── load_rag_chunks.py          # Insert knowledge docs into rag_chunks
│   ├── provision_genie_space.py    # Create Genie space
│   ├── run_sql.py                  # SQL execution helper
│   └── knowledge_docs/             # Markdown files for RAG
│       ├── 01_india_underwriting_manual_excerpt.md
│       ├── 02_product_guide_india.md
│       └── 03_underwriting_checklist.md
│
└── scripts/                        # Local dev scripts (from template)
    ├── start_app.py                # Run locally with frontend
    ├── quickstart.py               # Interactive setup
    └── ...
```

---

## Built With

| Component | Source |
|-----------|--------|
| Agent framework | [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) |
| App template | [databricks/app-templates](https://github.com/databricks/app-templates) `agent-openai-agents-sdk-multiagent` |
| Development toolkit | [databricks-solutions/ai-dev-kit](https://github.com/databricks-solutions/ai-dev-kit) |
| Serving | MLflow ResponsesAgent (`@stream` / `@invoke`) |
| Deployment | Databricks Asset Bundles (DAB) |
| Data | Unity Catalog Delta tables, UC Functions, Genie, Vector Search |

---

## Architecture

```
                    ┌─────────────────────────────┐
                    │   Databricks App (FastAPI)   │
                    │  ┌───────────────────────┐  │
   Browser ────────►│  │  Workflow UI (HTML/JS) │  │
                    │  └───────────┬───────────┘  │
                    │              │ /invocations  │
                    │  ┌───────────▼───────────┐  │
                    │  │   Orchestrator Agent   │  │
                    │  │  (OpenAI Agents SDK)   │  │
                    │  └──┬──────┬──────┬──────┘  │
                    └─────┼──────┼──────┼─────────┘
                          │      │      │
              ┌───────────┘      │      └───────────┐
              ▼                  ▼                  ▼
     ┌────────────┐    ┌────────────┐    ┌────────────┐
     │ Genie MCP  │    │UC Functions│    │Vector Search│
     │ (Structured│    │ (Business  │    │   (RAG /    │
     │   data)    │    │   rules)   │    │   docs)     │
     └─────┬──────┘    └─────┬──────┘    └─────┬──────┘
           │                 │                 │
     ┌─────▼─────────────────▼─────────────────▼──────┐
     │              Unity Catalog                      │
     │  Delta tables │ UC Functions │ Volumes │ VS idx │
     └────────────────────────────────────────────────┘
```

---

## Synthetic Data Disclaimer

All data in this demo is **synthetic** and generated for demonstration purposes only. No real personal information, medical records, or financial data is used. Outputs from the AI agent are **not** binding underwriting decisions.
