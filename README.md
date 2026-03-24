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

## Quick Start

### Step 0: Get the repo onto your machine

**Option A — Git clone (recommended)**
```bash
git clone https://github.com/sarbaniAi/underwriting-agent.git
cd underwriting-agent
```

**Option B — Download ZIP (no git required)**
1. Go to https://github.com/sarbaniAi/underwriting-agent
2. Click the green **Code** button > **Download ZIP**
3. Unzip and `cd underwriting-agent-main`

**Option C — Databricks Repos (run entirely from workspace)**
1. In your Databricks workspace, go to **Workspace > Repos**
2. Click **Add Repo**
3. Paste URL: `https://github.com/sarbaniAi/underwriting-agent.git`
4. Click **Create Repo**
5. Open a terminal in the workspace: **Clusters > your cluster > Web Terminal**, or use a notebook with `%sh`

**Option D — Databricks CLI import (upload from local to workspace)**
```bash
# First clone locally, then push to workspace
git clone https://github.com/sarbaniAi/underwriting-agent.git
databricks workspace import-dir ./underwriting-agent /Workspace/Users/<your-email>/underwriting-agent --profile <your-profile> --overwrite
```

### Step 1: Set up Databricks CLI authentication

If you don't have the Databricks CLI installed:
```bash
# macOS
brew install databricks

# or pip
pip install databricks-cli

# or see: https://docs.databricks.com/dev-tools/cli/install.html
```

Create an authenticated profile:
```bash
databricks auth login --host https://<your-workspace>.cloud.databricks.com --profile my-profile
```

Verify it works:
```bash
databricks auth describe --profile my-profile
```

### Step 2: Configure BOTH files before running install

You must edit **two files** before running the install. Use the checklist below.

#### File 1: `.env`

```bash
cp .env.example .env
```

Open `.env` in any editor and set these 4 values:

| Line | What to change | Where to find it |
|------|----------------|------------------|
| `DATABRICKS_CONFIG_PROFILE=` | Your CLI profile name (from Step 1) | The `--profile` name you used in `databricks auth login` |
| `UC_CATALOG=` | Your Unity Catalog catalog name | Workspace UI > **Catalog** > pick your catalog |
| `UC_SCHEMA=` | Schema name (default `underwriting_demo` is fine) | Will be created if it doesn't exist |
| `DATABRICKS_SQL_WAREHOUSE_ID=` | Your SQL warehouse ID | Workspace UI > **SQL Warehouses** > your warehouse > **Connection Details** > last segment of the **HTTP Path** |

Example `.env` after editing:
```env
DATABRICKS_CONFIG_PROFILE=my-profile
UC_CATALOG=my_catalog
UC_SCHEMA=underwriting_demo
DATABRICKS_SQL_WAREHOUSE_ID=665b042918235846

# Leave these blank — install.sh fills them automatically
GENIE_SPACE_ID=
MLFLOW_EXPERIMENT_ID=
VS_INDEX=my_catalog.underwriting_demo.rag_idx

# Optional — change the model if desired
ORCHESTRATOR_MODEL=databricks-claude-sonnet-4-5
```

#### File 2: `databricks.yml`

Open `databricks.yml` and change **3 things**:

| Line | What to change | Example |
|------|----------------|---------|
| `variables.catalog.default` | Same catalog as `.env` | `"my_catalog"` |
| `variables.warehouse_id.default` | Same warehouse ID as `.env` | `"665b042918235846"` |
| `targets.dev.workspace.host` | Your workspace URL | `https://dbc-ef54f790-f71c.cloud.databricks.com` |
| `targets.prod.workspace.host` | Same workspace URL (or prod workspace) | `https://dbc-ef54f790-f71c.cloud.databricks.com` |

Look for lines marked with `# CHANGE` — those are the ones to update.

#### Pre-flight checklist

Before running install, verify all of these:

- [ ] `.env` — `DATABRICKS_CONFIG_PROFILE` is set to your profile name (NOT `DEFAULT` unless that's your actual profile)
- [ ] `.env` — `UC_CATALOG` matches an existing catalog in your workspace (check in Catalog Explorer)
- [ ] `.env` — `UC_SCHEMA` is set (default `underwriting_demo` is fine — it will be created)
- [ ] `.env` — `DATABRICKS_SQL_WAREHOUSE_ID` is correct (from SQL Warehouses > Connection Details > HTTP Path)
- [ ] `databricks.yml` — `variables.catalog.default` matches your `.env` `UC_CATALOG`
- [ ] `databricks.yml` — `variables.warehouse_id.default` matches your `.env` `DATABRICKS_SQL_WAREHOUSE_ID`
- [ ] `databricks.yml` — `targets.dev.workspace.host` is your workspace URL
- [ ] `databricks.yml` — `targets.prod.workspace.host` is your workspace URL
- [ ] CLI auth works: `databricks auth describe --profile <your-profile>` shows your workspace host
- [ ] SQL warehouse is **running** (not stopped/paused)

### Step 3: Run the install script

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

### Step 4: Grant permissions + set up Vector Search

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
