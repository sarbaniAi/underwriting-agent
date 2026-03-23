-- India life insurance underwriting demo (synthetic)
-- All references use __CATALOG__.__SCHEMA__ which run_sql.py replaces at runtime.

-- Unstructured knowledge store (UC Volume)
CREATE VOLUME IF NOT EXISTS __CATALOG__.__SCHEMA__.knowledge_docs
COMMENT 'Synthetic manuals and guides for RAG / Knowledge Assistant demo';

-- Idempotent teardown (child tables first)
DROP TABLE IF EXISTS __CATALOG__.__SCHEMA__.fact_underwriting_decision;
DROP TABLE IF EXISTS __CATALOG__.__SCHEMA__.fact_application;
DROP TABLE IF EXISTS __CATALOG__.__SCHEMA__.dim_applicant;
DROP TABLE IF EXISTS __CATALOG__.__SCHEMA__.ref_underwriting_limits;
DROP TABLE IF EXISTS __CATALOG__.__SCHEMA__.ref_reason_code;
DROP TABLE IF EXISTS __CATALOG__.__SCHEMA__.dim_product;
DROP TABLE IF EXISTS __CATALOG__.__SCHEMA__.underwriter_workspace;

CREATE TABLE __CATALOG__.__SCHEMA__.dim_product (
  product_id STRING NOT NULL,
  product_name STRING NOT NULL,
  product_line STRING NOT NULL COMMENT 'term, traditional_participating, ulip',
  channel STRING NOT NULL COMMENT 'agency, banca, online',
  active_flag BOOLEAN NOT NULL
) USING DELTA COMMENT 'Synthetic product master — India demo';

CREATE TABLE __CATALOG__.__SCHEMA__.ref_reason_code (
  reason_code STRING NOT NULL,
  category STRING NOT NULL COMMENT 'medical, financial, disclosure, other',
  description STRING NOT NULL
) USING DELTA COMMENT 'Synthetic decline / postpone reason codes';

CREATE TABLE __CATALOG__.__SCHEMA__.ref_underwriting_limits (
  product_id STRING NOT NULL,
  age_min INT NOT NULL,
  age_max INT NOT NULL,
  max_sum_assured_inr BIGINT NOT NULL COMMENT 'Maximum sum assured in INR',
  smoker_allowed BOOLEAN NOT NULL
) USING DELTA COMMENT 'Synthetic age and sum-assured limits by product';

CREATE TABLE __CATALOG__.__SCHEMA__.dim_applicant (
  applicant_id STRING NOT NULL,
  birth_year INT NOT NULL,
  gender STRING NOT NULL,
  smoker_status STRING NOT NULL COMMENT 'never, former, current',
  state_ut STRING NOT NULL COMMENT 'Indian state/UT code',
  occupation_class STRING NOT NULL COMMENT '1=desk, 2=light manual, etc.',
  bmi_bucket STRING NOT NULL
) USING DELTA COMMENT 'Synthetic applicant demographics — no real PII';

CREATE TABLE __CATALOG__.__SCHEMA__.fact_application (
  application_id STRING NOT NULL,
  applicant_id STRING NOT NULL,
  product_id STRING NOT NULL,
  application_date DATE NOT NULL,
  status STRING NOT NULL COMMENT 'submitted, in_review, approved, declined, postponed',
  channel STRING NOT NULL
) USING DELTA COMMENT 'Synthetic applications';

CREATE TABLE __CATALOG__.__SCHEMA__.fact_underwriting_decision (
  decision_id STRING NOT NULL,
  application_id STRING NOT NULL,
  decision_date DATE NOT NULL,
  outcome STRING NOT NULL COMMENT 'approved, declined, postponed, referred',
  reason_code STRING,
  sum_assured_inr BIGINT NOT NULL,
  approved_risk_class STRING NOT NULL COMMENT 'preferred, standard, substandard'
) USING DELTA COMMENT 'Synthetic underwriting outcomes';

CREATE TABLE __CATALOG__.__SCHEMA__.underwriter_workspace (
  workspace_id STRING NOT NULL,
  application_id STRING NOT NULL,
  analyst_name STRING,
  risk_class_override STRING,
  substandard_rating DOUBLE,
  coverage_approved_inr BIGINT,
  ai_recommendation STRING,
  analyst_notes STRING,
  status STRING,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
) USING DELTA COMMENT 'Underwriter workflow workspace — analyst decisions and AI recommendations';

INSERT INTO __CATALOG__.__SCHEMA__.dim_product VALUES
  ('PRD-TERM-001', 'Bharat Term Secure Plus', 'term', 'online', true),
  ('PRD-TRAD-002', 'India Life Sanchay Participating', 'traditional_participating', 'agency', true),
  ('PRD-ULIP-003', 'Flexi Growth ULIP', 'ulip', 'banca', true);

INSERT INTO __CATALOG__.__SCHEMA__.ref_reason_code VALUES
  ('R-MED-01', 'medical', 'Elevated risk indicators in medical questionnaire'),
  ('R-FIN-02', 'financial', 'Income documentation incomplete for proposed sum assured'),
  ('R-DISC-03', 'disclosure', 'Material fact not disclosed at application stage'),
  ('R-OTH-99', 'other', 'Referred for manual review — avocation or hobby disclosure');

INSERT INTO __CATALOG__.__SCHEMA__.ref_underwriting_limits VALUES
  ('PRD-TERM-001', 18, 65, 20000000, true),
  ('PRD-TRAD-002', 0, 60, 15000000, true),
  ('PRD-ULIP-003', 18, 55, 10000000, false);

INSERT INTO __CATALOG__.__SCHEMA__.dim_applicant VALUES
  ('APP-00001', 1988, 'F', 'never', 'MH', '1', 'normal'),
  ('APP-00002', 1995, 'M', 'never', 'KA', '2', 'overweight'),
  ('APP-00003', 1982, 'M', 'current', 'TN', '2', 'normal'),
  ('APP-00004', 1990, 'F', 'never', 'DL', '1', 'normal'),
  ('APP-00005', 1978, 'M', 'former', 'GJ', '3', 'obese');

INSERT INTO __CATALOG__.__SCHEMA__.fact_application VALUES
  ('APL-10001', 'APP-00001', 'PRD-TERM-001', DATE '2025-01-10', 'approved', 'online'),
  ('APL-10002', 'APP-00002', 'PRD-TRAD-002', DATE '2025-01-12', 'in_review', 'agency'),
  ('APL-10003', 'APP-00003', 'PRD-TERM-001', DATE '2025-01-15', 'declined', 'online'),
  ('APL-10004', 'APP-00004', 'PRD-ULIP-003', DATE '2025-02-01', 'approved', 'banca'),
  ('APL-10005', 'APP-00005', 'PRD-TRAD-002', DATE '2025-02-05', 'postponed', 'agency');

INSERT INTO __CATALOG__.__SCHEMA__.fact_underwriting_decision VALUES
  ('DEC-90001', 'APL-10001', DATE '2025-01-11', 'approved', NULL, 1500000, 'preferred'),
  ('DEC-90002', 'APL-10002', DATE '2025-01-14', 'approved', NULL, 800000, 'standard'),
  ('DEC-90003', 'APL-10003', DATE '2025-01-16', 'declined', 'R-MED-01', 0, 'substandard'),
  ('DEC-90004', 'APL-10004', DATE '2025-02-02', 'approved', NULL, 500000, 'standard'),
  ('DEC-90005', 'APL-10005', DATE '2025-02-07', 'postponed', 'R-FIN-02', 0, 'substandard');
