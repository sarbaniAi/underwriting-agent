#!/bin/bash
# ============================================================================
# India Underwriting Agent — Full Installation Script
#
# This script sets up the entire demo stack in a customer's Databricks workspace:
#   1. Delta tables + seed data
#   2. UC functions (governed underwriting rules)
#   3. RAG chunks table + knowledge doc content
#   4. Upload knowledge docs to UC Volume
#   5. Genie space
#   6. Vector Search endpoint + index (manual step — printed at end)
#   7. Grant app service principal permissions
#   8. Deploy the Databricks App via DAB
#
# Prerequisites: .env file configured (copy from .env.example)
# ============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load .env from project root
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a; source "$PROJECT_DIR/.env"; set +a
    echo "Loaded .env from $PROJECT_DIR/.env"
else
    echo "ERROR: No .env file found at $PROJECT_DIR/.env"
    echo "Copy .env.example to .env and fill in your values first."
    exit 1
fi

PROFILE="${DATABRICKS_CONFIG_PROFILE:-DEFAULT}"
CATALOG="${UC_CATALOG:?Set UC_CATALOG in .env}"
SCHEMA="${UC_SCHEMA:?Set UC_SCHEMA in .env}"
WAREHOUSE="${DATABRICKS_SQL_WAREHOUSE_ID:?Set DATABRICKS_SQL_WAREHOUSE_ID in .env}"

echo ""
echo "============================================"
echo "  India Underwriting Agent — Installation"
echo "============================================"
echo "  Profile:   $PROFILE"
echo "  Catalog:   $CATALOG"
echo "  Schema:    $SCHEMA"
echo "  Warehouse: $WAREHOUSE"
echo "============================================"
echo ""

# Verify auth
echo "Step 0: Verifying Databricks CLI auth..."
databricks auth describe --profile "$PROFILE" 2>&1 | head -3
echo ""

# Step 1: Create tables + seed data
echo "Step 1: Creating tables and seeding data..."
cd "$SCRIPT_DIR"
python3 run_sql.py setup_underwriting_demo.sql
echo ""

# Step 2: Create UC functions + RAG chunks table
echo "Step 2: Creating UC functions and RAG chunks table..."
python3 run_sql.py provision_stack.sql
echo ""

# Step 3: Load knowledge docs into RAG chunks
echo "Step 3: Loading knowledge docs into rag_chunks..."
python3 load_rag_chunks.py
echo ""

# Step 4: Upload knowledge docs to UC Volume
echo "Step 4: Uploading knowledge docs to UC Volume..."
cd /tmp
databricks fs cp --recursive "$SCRIPT_DIR/knowledge_docs/" \
    "dbfs:/Volumes/$CATALOG/$SCHEMA/knowledge_docs/" \
    --profile "$PROFILE" --overwrite 2>&1 || echo "  (Volume upload may need manual step — see README)"
echo ""

# Step 5: Create Genie space
echo "Step 5: Creating Genie space..."
cd "$SCRIPT_DIR"
python3 provision_genie_space.py
GENIE_ID=""
if [ -f genie_space_id.txt ]; then
    GENIE_ID=$(cat genie_space_id.txt | tr -d '[:space:]')
    echo "  Genie space created: $GENIE_ID"
    # Update .env with new Genie space ID
    if grep -q "^GENIE_SPACE_ID=" "$PROJECT_DIR/.env"; then
        sed -i.bak "s/^GENIE_SPACE_ID=.*/GENIE_SPACE_ID=$GENIE_ID/" "$PROJECT_DIR/.env"
    fi
fi
echo ""

# Step 6: Create MLflow experiment + update databricks.yml
echo "Step 6: Creating MLflow experiment..."
cd "$PROJECT_DIR"
USER_EMAIL=$(databricks auth describe --profile "$PROFILE" 2>&1 | grep "User:" | awk '{print $2}')
EXP_PATH="/Users/${USER_EMAIL}/underwriting-agent"
EXP_RESULT=$(databricks experiments create-experiment "$EXP_PATH" --profile "$PROFILE" 2>&1 || true)
EXP_ID=$(echo "$EXP_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('experiment_id',''))" 2>/dev/null || echo "")

if [ -z "$EXP_ID" ]; then
    # Experiment may already exist — try to get by name
    EXP_ID=$(databricks experiments get-by-name "$EXP_PATH" --profile "$PROFILE" 2>&1 | python3 -c "import sys,json; print(json.load(sys.stdin).get('experiment',{}).get('experiment_id',''))" 2>/dev/null || echo "")
fi

if [ -n "$EXP_ID" ]; then
    echo "  MLflow experiment ID: $EXP_ID"
    # Update databricks.yml with experiment ID
    sed -i.bak "s/experiment_id: \"[^\"]*\"/experiment_id: \"$EXP_ID\"/" "$PROJECT_DIR/databricks.yml"
    # Update .env
    if grep -q "^MLFLOW_EXPERIMENT_ID=" "$PROJECT_DIR/.env"; then
        sed -i.bak "s/^MLFLOW_EXPERIMENT_ID=.*/MLFLOW_EXPERIMENT_ID=$EXP_ID/" "$PROJECT_DIR/.env"
    fi
else
    echo "  WARNING: Could not create/find MLflow experiment. You may need to set experiment_id manually in databricks.yml"
fi
echo ""

# Step 7: Deploy app
echo "Step 7: Deploying Databricks App..."
DATABRICKS_CONFIG_PROFILE="$PROFILE" databricks bundle deploy
echo ""

echo "Step 8: Starting app..."
DATABRICKS_CONFIG_PROFILE="$PROFILE" databricks bundle run underwriting_agent
echo ""

echo "============================================"
echo "  Installation complete!"
echo "============================================"
echo ""
echo "MANUAL STEPS REMAINING:"
echo ""
echo "1. VECTOR SEARCH (if not already set up):"
echo "   - Go to workspace UI > Compute > Vector Search"
echo "   - Create endpoint: 'underwriter_vs_endpoint'"
echo "   - Create index: '$CATALOG.$SCHEMA.rag_idx'"
echo "     Source table: '$CATALOG.$SCHEMA.rag_chunks'"
echo "     Sync mode: DELTA_SYNC (triggered)"
echo "     Embedding: databricks-gte-large-en"
echo "     Columns: content (to embed), source_path (metadata)"
echo ""
echo "2. GRANT APP PERMISSIONS:"
echo "   Run: bash $SCRIPT_DIR/grant_permissions.sh"
echo "   (After the app is deployed and its service principal is created)"
echo ""
echo "3. UPDATE .env if Genie space ID changed:"
echo "   Current: GENIE_SPACE_ID=$GENIE_ID"
echo ""
