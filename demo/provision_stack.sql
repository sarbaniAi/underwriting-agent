-- UC functions + RAG chunks table. Uses __CATALOG__.__SCHEMA__ placeholder.

DROP TABLE IF EXISTS __CATALOG__.__SCHEMA__.rag_chunks;

CREATE TABLE __CATALOG__.__SCHEMA__.rag_chunks (
  chunk_id STRING NOT NULL,
  source_path STRING NOT NULL,
  content STRING NOT NULL
) USING DELTA
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'comment' = 'Synthetic underwriting manuals for retrieval (demo)'
);

CREATE OR REPLACE FUNCTION __CATALOG__.__SCHEMA__.fn_max_sum_assured_inr(pid STRING, age_years INT)
RETURNS BIGINT
LANGUAGE SQL
RETURN (
  SELECT MAX(l.max_sum_assured_inr)
  FROM __CATALOG__.__SCHEMA__.ref_underwriting_limits AS l
  WHERE l.product_id = pid
    AND age_years BETWEEN l.age_min AND l.age_max
);

CREATE OR REPLACE FUNCTION __CATALOG__.__SCHEMA__.fn_risk_tier(bmi_bucket STRING, smoker_status STRING)
RETURNS STRING
LANGUAGE SQL
RETURN (
  CASE
    WHEN smoker_status = 'current' THEN 'high'
    WHEN bmi_bucket = 'obese' THEN 'elevated'
    WHEN bmi_bucket = 'overweight' THEN 'moderate'
    ELSE 'standard'
  END
);

CREATE OR REPLACE FUNCTION __CATALOG__.__SCHEMA__.fn_ulip_smoker_blocked(pid STRING, smoker_status STRING)
RETURNS BOOLEAN
LANGUAGE SQL
RETURN (
  pid = 'PRD-ULIP-003' AND smoker_status = 'current'
);
