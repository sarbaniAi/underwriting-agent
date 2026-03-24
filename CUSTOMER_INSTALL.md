# Customer Installation Guide (Production Workspace)

Use this guide when the customer **already has their data, UC functions, Genie space, and Vector Search** set up in their workspace. This skips all demo data creation scripts.

> If starting from scratch with synthetic demo data, use `demo/install.sh` instead — see [README.md](./README.md).

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| Databricks workspace | Enterprise or Premium with Unity Catalog enabled |
| Databricks CLI | v0.200+ installed. [Install guide](https://docs.databricks.com/dev-tools/cli/install.html) |
| Unity Catalog | Catalog + schema with tables for applicants, applications, decisions, products |
| UC Functions | Underwriting rule functions registered in the same schema |
| Genie Space | Configured over the underwriting tables |
| Vector Search | Endpoint + index over policy/manual documents |
| SQL Warehouse | Running warehouse (serverless or classic) |

---

## Step 1: Clone the repo

```bash
git clone https://github.com/sarbaniAi/underwriting-agent.git
cd underwriting-agent
```

## Step 2: Set up Databricks CLI authentication

```bash
databricks auth login --host https://<your-workspace>.cloud.databricks.com --profile my-profile
databricks auth describe --profile my-profile   # verify it works
```

## Step 3: Configure `.env`

```bash
cp .env.example .env
```

Edit `.env` with your workspace values:

| Field | Value |
|-------|-------|
| `DATABRICKS_CONFIG_PROFILE` | Your CLI profile name from Step 2 |
| `UC_CATALOG` | Your Unity Catalog catalog name |
| `UC_SCHEMA` | Your schema containing underwriting tables |
| `DATABRICKS_SQL_WAREHOUSE_ID` | SQL Warehouse ID (from SQL Warehouses > Connection Details > HTTP Path, last segment) |
| `GENIE_SPACE_ID` | Your Genie space ID (from the Genie space URL) |
| `VS_INDEX` | Full name of your Vector Search index (e.g. `catalog.schema.index_name`) |
| `VS_ENDPOINT` | Your Vector Search endpoint name |
| `ORCHESTRATOR_MODEL` | LLM model (default: `databricks-claude-sonnet-4-5`) |
| `COMPANY_NAME` | Your company name (displayed in the UI sidebar and agent prompt) |

## Step 4: Configure `databricks.yml`

Open `databricks.yml` and update lines marked with `# CHANGE`:

| Field | Location in file |
|-------|-----------------|
| `variables.catalog.default` | Must match `UC_CATALOG` in `.env` |
| `variables.warehouse_id.default` | Must match `DATABRICKS_SQL_WAREHOUSE_ID` in `.env` |
| `variables.genie_space_id.default` | Must match `GENIE_SPACE_ID` in `.env` |
| `variables.company_name.default` | Must match `COMPANY_NAME` in `.env` |
| `targets.dev.workspace.host` | Your workspace URL |
| `targets.prod.workspace.host` | Your workspace URL (or production workspace) |

## Step 5: Configure `app.yaml`

Open `app.yaml` and update the env var values to match your `.env`:

| Env var | Value |
|---------|-------|
| `UC_CATALOG` | Your catalog |
| `UC_SCHEMA` | Your schema |
| `DATABRICKS_WAREHOUSE_ID` | Your warehouse ID |
| `GENIE_SPACE_ID` | Your Genie space ID |
| `VS_INDEX` | Your Vector Search index name |
| `ORCHESTRATOR_MODEL` | Your preferred LLM model |
| `COMPANY_NAME` | Your company name |

## Step 6: Create MLflow experiment

```bash
databricks experiments create-experiment "/Users/<your-email>/underwriting-agent" --profile my-profile
```

Copy the returned `experiment_id` and set it in:
- `databricks.yml` → `resources.apps.underwriting_agent.resources[0].experiment.experiment_id`
- `app.yaml` → `MLFLOW_EXPERIMENT_ID` value

## Step 7: Deploy the app

```bash
# Using DAB (recommended for Enterprise/Premium workspaces)
DATABRICKS_CONFIG_PROFILE=my-profile databricks bundle deploy
DATABRICKS_CONFIG_PROFILE=my-profile databricks bundle run underwriting_agent
```

> **If DAB deploy fails** (permission error on Free Edition), use manual deploy:
> ```bash
> databricks apps create underwriting-agent --profile my-profile
> # Wait for app compute to start, then:
> databricks apps deploy underwriting-agent --source-code-path /Workspace/Users/<your-email>/.bundle/underwriting_agent/dev/files --profile my-profile
> ```

## Step 8: Grant app permissions

```bash
bash demo/grant_permissions.sh
```

This grants the app's service principal access to:
- Unity Catalog (catalog, schema, tables, functions, volumes)
- SQL Warehouse
- Genie Space
- MLflow Experiment

## Step 9: Open and verify

Open the app URL (printed at the end of Step 7) and test:

1. Select an applicant from the dropdown
2. Select an application
3. Click **Analyze Application** — the AI should call Genie, UC functions, and Vector Search
4. Try the 4 decision buttons (Approve / Deny / Approve with Changes / Request Information)
5. Verify decisions are saved (check the Decision History section)

---

## What to customize in `agent_server/agent.py`

If your table schemas or UC function signatures differ from the demo, update these sections:

### UC Function tools (lines ~85-130)
Update SQL queries and function parameters to match your actual UC functions:
```python
@function_tool
async def check_max_sum_assured(product_id: str, age_years: int) -> str:
    # Update the SQL to call YOUR UC function with YOUR parameter names
    val = await _exec_sql(f"SELECT {CATALOG}.{SCHEMA}.your_function_name('{product_id}', {age_years})")
```

### Vector Search tool (lines ~135-165)
Update column names if your VS index uses different columns:
```python
result = _ws.vector_search_indexes.query_index(
    index_name=VS_INDEX,
    query_text=query,
    columns=["your_content_column", "your_source_column"],  # CHANGE these
    num_results=5,
)
```

### Orchestrator instructions (lines ~195-240)
Update the `ORCHESTRATOR_INSTRUCTIONS` string to describe YOUR tools and data:
- What each tool does
- What data sources are available
- When to use which tool

### Workflow API (agent_server/workflow_api.py)
Update SQL queries if your table/column names differ:
- `list_applicants()` — query for applicant dropdown
- `get_application()` — join query for application detail
- `list_applications()` — applications for an applicant
- `save_workspace()` — MERGE into decision table

---

## Architecture (what runs where)

```
Customer opens app URL
    → FastAPI serves workflow UI (HTML/JS)
    → User selects applicant + clicks "Analyze Application"
    → Frontend calls POST /invocations
    → Orchestrator agent decides which tool(s) to call:
        ├── Genie MCP   → queries structured tables via Genie space
        ├── UC Functions → executes governed SQL functions via warehouse
        └── Vector Search → searches policy documents via VS index
    → AI response rendered in markdown
    → User makes decision (Approve/Deny/etc.)
    → Frontend calls POST /api/workspace → saved to Delta table
    → Decision also updates fact_underwriting_decision + fact_application
```

---

## Files the customer does NOT need

| File/Directory | Purpose | Needed? |
|---------------|---------|---------|
| `demo/install.sh` | Creates demo data from scratch | No — data exists |
| `demo/setup_underwriting_demo.sql` | Table DDL + seed data | No |
| `demo/provision_stack.sql` | UC functions + rag_chunks table | No |
| `demo/load_rag_chunks.py` | Loads markdown into rag_chunks | No |
| `demo/provision_genie_space.py` | Creates Genie space | No |
| `demo/run_sql.py` | SQL helper for setup scripts | No |
| `demo/knowledge_docs/` | Sample policy documents | No |
| `demo/grant_permissions.sh` | Grants app SP permissions | **Yes — run this** |
