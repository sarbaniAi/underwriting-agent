"""
India Retail Life Insurance Underwriting Assistant — Multi-Agent Orchestrator.

Built from: databricks app-templates / agent-openai-agents-sdk-multiagent
Toolkit:    databricks ai-dev-kit (skills + tools-core patterns)

Architecture:
  Orchestrator (OpenAI Agents SDK)
    ├── Genie MCP      → "India Underwriter" Genie space (NL queries over
    │                     applicants, applications, decisions, products, limits)
    ├── UC Functions    → fn_max_sum_assured_inr, fn_risk_tier, fn_ulip_smoker_blocked
    │                     (governed business rules exposed as catalog functions)
    └── Vector Search   → RAG over underwriting manuals & policy documents
                          (rag_idx on knowledge_docs volume)

Data never leaves the workspace. All tables, functions, and indexes live in
Unity Catalog under the configured catalog and schema (set via UC_CATALOG and UC_SCHEMA env vars).
"""

import litellm
import logging
import os
from contextlib import nullcontext
from typing import AsyncGenerator

import mlflow
from agents import Agent, Runner, function_tool, set_default_openai_api, set_default_openai_client
from agents.tracing import set_trace_processors
from databricks.sdk import WorkspaceClient
from databricks_openai import AsyncDatabricksOpenAI
from databricks_openai.agents import McpServer
from mlflow.genai.agent_server import invoke, stream
from mlflow.types.responses import (
    ResponsesAgentRequest,
    ResponsesAgentResponse,
    ResponsesAgentStreamEvent,
)

from agent_server.utils import (
    build_mcp_url,
    get_session_id,
    process_agent_stream_events,
)

# ---------------------------------------------------------------------------
# Configuration (from environment / .env)
# ---------------------------------------------------------------------------

CATALOG = os.environ.get("UC_CATALOG", "serverless_stable_tcrn2v_catalog")
SCHEMA = os.environ.get("UC_SCHEMA", "underwriting_demo")
GENIE_SPACE_ID = os.environ.get("GENIE_SPACE_ID", "01f125d0813316d8adac3002ca0f0658")
VS_INDEX = os.environ.get("VS_INDEX", f"{CATALOG}.{SCHEMA}.rag_idx")
WAREHOUSE_ID = os.environ.get("DATABRICKS_WAREHOUSE_ID", "91dbe14a27ddabad")
MODEL = os.environ.get("ORCHESTRATOR_MODEL", "databricks-claude-sonnet-4-5")
COMPANY_NAME = os.environ.get("COMPANY_NAME", "India Life")

# ---------------------------------------------------------------------------
# Client setup
# ---------------------------------------------------------------------------

set_default_openai_client(AsyncDatabricksOpenAI())
set_default_openai_api("chat_completions")
set_trace_processors([])  # only use mlflow for trace processing
mlflow.openai.autolog()
logging.getLogger("mlflow.utils.autologging_utils").setLevel(logging.ERROR)
litellm.suppress_debug_info = True

_ws = WorkspaceClient()

# ---------------------------------------------------------------------------
# Helper: execute a UC SQL function
# ---------------------------------------------------------------------------


async def _exec_sql(sql: str) -> str:
    """Execute SQL via Statement Execution API and return the first cell."""
    from databricks.sdk.service.sql import Disposition, StatementState

    resp = _ws.statement_execution.execute_statement(
        warehouse_id=WAREHOUSE_ID,
        statement=sql,
        wait_timeout="30s",
        disposition=Disposition.INLINE,
    )
    if resp.status.state != StatementState.SUCCEEDED:
        return f"Error: {resp.status.error.message if resp.status.error else 'Query failed'}"
    if resp.result and resp.result.data_array:
        return str(resp.result.data_array[0][0])
    return "No result returned."


# ---------------------------------------------------------------------------
# Tool 1: UC Functions (governed underwriting rules)
# ---------------------------------------------------------------------------


@function_tool
async def check_max_sum_assured(product_id: str, age_years: int) -> str:
    """Check the maximum sum assured (in INR) for a given product ID and applicant age.
    Use when asked about coverage limits, maximum insurable amount, or
    product-specific sum-assured caps.
    Parameters: product_id (e.g. 'ULIP-01'), age_years (integer)."""
    val = await _exec_sql(
        f"SELECT {CATALOG}.{SCHEMA}.fn_max_sum_assured_inr('{product_id}', {age_years})"
    )
    return f"Maximum sum assured for product {product_id}, age {age_years}: INR {val}"


@function_tool
async def get_risk_tier(bmi_bucket: str, smoker_status: str) -> str:
    """Determine the risk tier (Preferred / Standard / Substandard) for an
    applicant based on BMI bucket and smoking status.
    Parameters:
      bmi_bucket: one of 'underweight', 'normal', 'overweight', 'obese'
      smoker_status: one of 'smoker', 'non-smoker'
    Use when asked about risk classification or tier assignment."""
    val = await _exec_sql(
        f"SELECT {CATALOG}.{SCHEMA}.fn_risk_tier('{bmi_bucket}', '{smoker_status}')"
    )
    return f"Risk tier for BMI bucket={bmi_bucket}, smoker_status={smoker_status}: {val}"


@function_tool
async def check_ulip_smoker_blocked(product_id: str, smoker_status: str) -> str:
    """Check whether a ULIP product blocks smoker applicants.
    Use when asked if a smoker can buy a specific ULIP product.
    Parameters:
      product_id: e.g. 'ULIP-01'
      smoker_status: one of 'smoker', 'non-smoker'"""
    val = await _exec_sql(
        f"SELECT {CATALOG}.{SCHEMA}.fn_ulip_smoker_blocked('{product_id}', '{smoker_status}')"
    )
    blocked = str(val).lower() in ("true", "1", "yes")
    if blocked:
        return f"BLOCKED: Product {product_id} does not accept applicants with smoker_status={smoker_status}."
    return f"ALLOWED: Product {product_id} accepts applicants with smoker_status={smoker_status}."


# ---------------------------------------------------------------------------
# Tool 2: Vector Search RAG (underwriting manuals & policy docs)
# ---------------------------------------------------------------------------


@function_tool
async def search_underwriting_docs(query: str) -> str:
    """Search underwriting manuals, policy guidelines, and procedural documents.
    Use for questions about underwriting policies, exclusions, medical requirements,
    standard procedures, or any narrative/textual policy content."""
    try:
        result = _ws.vector_search_indexes.query_index(
            index_name=VS_INDEX,
            query_text=query,
            columns=["content", "source_document"],
            num_results=5,
        )
        if not result.result or not result.result.data_array:
            return "No relevant documents found."

        columns = [c.name for c in result.manifest.columns]
        chunks, sources = [], set()
        for row in result.result.data_array:
            r = dict(zip(columns, row))
            chunks.append(r.get("content", ""))
            if r.get("source_document"):
                sources.add(r["source_document"])

        context = "\n\n---\n\n".join(chunks)
        src = ", ".join(sources) if sources else "underwriting knowledge base"
        return f"Sources: {src}\n\n{context}"
    except Exception as e:
        return f"Vector search error: {e}"


# ---------------------------------------------------------------------------
# MCP: Genie space (structured data queries)
# ---------------------------------------------------------------------------


async def init_genie_mcp():
    """Create the Genie MCP server for structured data queries."""
    if not GENIE_SPACE_ID:
        return nullcontext()
    return McpServer(
        url=build_mcp_url(f"/api/2.0/mcp/genie/{GENIE_SPACE_ID}"),
        name=(
            f"Query the {COMPANY_NAME} Underwriter Genie space for structured data: "
            "applicant profiles, application details, underwriting decisions, "
            "product catalogue, reason codes, and underwriting limits. "
            "Use for any question about specific applicants, applications, "
            "decision history, or aggregate data queries."
        ),
    )


# ---------------------------------------------------------------------------
# Orchestrator agent
# ---------------------------------------------------------------------------

ORCHESTRATOR_INSTRUCTIONS = f"""\
You are a {COMPANY_NAME} retail life insurance underwriting assistant.
You help analysts and underwriters explore applications, rules, and policy context
using company data and documents. You do NOT make binding underwriting decisions.

DATA IS SYNTHETIC. All outputs are for demonstration purposes only.

AVAILABLE TOOLS — choose the right one for each question:

1. **Genie MCP tools** — for structured data queries:
   - Applicant profiles (dim_applicant)
   - Application details (fact_application)
   - Underwriting decisions (fact_underwriting_decision)
   - Product catalogue (dim_product)
   - Reason codes (ref_reason_code)
   - Underwriting limits (ref_underwriting_limits)
   Use for: "Show me applicant X", "How many applications were declined?",
   "What products do we offer?", "List decisions for application Y"

2. **check_max_sum_assured(product_id, age_years)** — governed UC function
   Use for: "What is the max sum assured for product ULIP-01, age 35?"

3. **get_risk_tier(bmi_bucket, smoker_status)** — governed UC function
   bmi_bucket: 'underweight'/'normal'/'overweight'/'obese'
   smoker_status: 'smoker'/'non-smoker'
   Use for: "What risk tier for an overweight smoker?"

4. **check_ulip_smoker_blocked(product_id, smoker_status)** — governed UC function
   Use for: "Can a smoker buy ULIP product ULIP-01?"

5. **search_underwriting_docs** — RAG over policy documents
   Use for: "What does the manual say about diabetes?",
   "Medical requirements for sum assured above 1 crore?",
   "Explain exclusion policy for pre-existing conditions"

RESPONSE FORMAT:
- Lead with a clear **Summary** answer
- Include a **What was queried** section showing which tool/data source was used
- Add **Caveats** where appropriate
- Always note: data is synthetic, outputs are not final underwriting decisions
"""


def create_orchestrator(mcp_server) -> Agent:
    return Agent(
        name="UnderwritingOrchestrator",
        instructions=ORCHESTRATOR_INSTRUCTIONS,
        model=MODEL,
        mcp_servers=[mcp_server] if mcp_server else [],
        tools=[
            check_max_sum_assured,
            get_risk_tier,
            check_ulip_smoker_blocked,
            search_underwriting_docs,
        ],
    )


# ---------------------------------------------------------------------------
# MLflow Responses API handlers
# ---------------------------------------------------------------------------


@invoke()
async def invoke_handler(request: ResponsesAgentRequest) -> ResponsesAgentResponse:
    if session_id := get_session_id(request):
        mlflow.update_current_trace(metadata={"mlflow.trace.session": session_id})
    async with await init_genie_mcp() as mcp_server:
        agent = create_orchestrator(mcp_server)
        messages = [i.model_dump() for i in request.input]
        result = await Runner.run(agent, messages)
        return ResponsesAgentResponse(output=[item.to_input_item() for item in result.new_items])


@stream()
async def stream_handler(request: ResponsesAgentRequest) -> AsyncGenerator[ResponsesAgentStreamEvent, None]:
    if session_id := get_session_id(request):
        mlflow.update_current_trace(metadata={"mlflow.trace.session": session_id})
    async with await init_genie_mcp() as mcp_server:
        agent = create_orchestrator(mcp_server)
        messages = [i.model_dump() for i in request.input]
        result = Runner.run_streamed(agent, input=messages)
        async for event in process_agent_stream_events(result.stream_events()):
            yield event
