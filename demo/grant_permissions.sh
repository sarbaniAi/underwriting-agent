#!/bin/bash
# Grant permissions to the Databricks App service principal.
# Run AFTER the app is deployed (databricks bundle deploy + run).
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a; source "$PROJECT_DIR/.env"; set +a
fi

PROFILE="${DATABRICKS_CONFIG_PROFILE:-DEFAULT}"
CATALOG="${UC_CATALOG:?Set UC_CATALOG}"
SCHEMA="${UC_SCHEMA:?Set UC_SCHEMA}"
WAREHOUSE="${DATABRICKS_SQL_WAREHOUSE_ID:?Set DATABRICKS_SQL_WAREHOUSE_ID}"
APP_NAME="${APP_NAME:-underwriting-agent}"

echo "Finding app service principal..."
SP=$(databricks apps get "$APP_NAME" --profile "$PROFILE" -o json 2>&1 | python3 -c "import sys,json; print(json.load(sys.stdin).get('service_principal_client_id',''))")

if [ -z "$SP" ]; then
    echo "ERROR: Could not find service principal for app '$APP_NAME'"
    echo "Make sure the app is deployed first: databricks bundle deploy && databricks bundle run underwriting_agent"
    exit 1
fi

echo "App service principal: $SP"
echo ""

echo "Granting Unity Catalog permissions..."
for SQL in \
    "GRANT USE CATALOG ON CATALOG $CATALOG TO \`$SP\`" \
    "GRANT USE SCHEMA ON SCHEMA $CATALOG.$SCHEMA TO \`$SP\`" \
    "GRANT SELECT ON SCHEMA $CATALOG.$SCHEMA TO \`$SP\`" \
    "GRANT MODIFY ON TABLE $CATALOG.$SCHEMA.underwriter_workspace TO \`$SP\`" \
    "GRANT MODIFY ON TABLE $CATALOG.$SCHEMA.fact_underwriting_decision TO \`$SP\`" \
    "GRANT MODIFY ON TABLE $CATALOG.$SCHEMA.fact_application TO \`$SP\`" \
    "GRANT EXECUTE ON FUNCTION $CATALOG.$SCHEMA.fn_max_sum_assured_inr TO \`$SP\`" \
    "GRANT EXECUTE ON FUNCTION $CATALOG.$SCHEMA.fn_risk_tier TO \`$SP\`" \
    "GRANT EXECUTE ON FUNCTION $CATALOG.$SCHEMA.fn_ulip_smoker_blocked TO \`$SP\`" \
    "GRANT READ VOLUME ON VOLUME $CATALOG.$SCHEMA.knowledge_docs TO \`$SP\`"
do
    RESULT=$(databricks api post /api/2.0/sql/statements --json "{\"warehouse_id\": \"$WAREHOUSE\", \"statement\": \"$SQL\", \"wait_timeout\": \"30s\"}" --profile "$PROFILE" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status',{}).get('state','UNKNOWN'))" 2>&1)
    echo "  $SQL => $RESULT"
done

echo ""
echo "Granting SQL warehouse permission..."
databricks api patch "/api/2.0/permissions/warehouses/$WAREHOUSE" --json "{
    \"access_control_list\": [{\"service_principal_name\": \"$SP\", \"permission_level\": \"CAN_USE\"}]
}" --profile "$PROFILE" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print('  Warehouse:', 'OK' if 'access_control_list' in d else d)" 2>&1

echo ""
echo "All permissions granted."
echo "If Vector Search is set up, also grant the VS endpoint permission:"
echo "  databricks api patch /api/2.0/permissions/serving-endpoints/<VS_ENDPOINT_NAME> --json '{\"access_control_list\": [{\"service_principal_name\": \"$SP\", \"permission_level\": \"CAN_QUERY\"}]}' --profile $PROFILE"
