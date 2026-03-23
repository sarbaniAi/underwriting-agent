# Underwriting Checklist — New Business (India, Demo)

Use this checklist when triaging inbound applications in the **underwriting_demo** environment.

## A — Data completeness

1. Applicant identity references are **synthetic** in demo tables (no Aadhaar/PAN collection).  
2. Product code must exist in **dim_product** (e.g. PRD-TERM-001, PRD-TRAD-002, PRD-ULIP-003).  
3. Application status in **fact_application** should reflect workflow: submitted → in_review → final.  

## B — Risk classification

1. Map **occupation_class** (1–3 in demo) to desk vs manual exposure.  
2. Map **bmi_bucket** (normal, overweight, obese) to medical tiering.  
3. **Smoker_status** must be consistent with product rules — ULIP demo rule excludes **current** smokers from simplified path.  

## C — Decisioning

1. **Approved** decisions require a non-null **sum_assured_inr** in **fact_underwriting_decision** when outcome is approved.  
2. **Declined** decisions should reference a **reason_code** from **ref_reason_code** where possible (e.g. R-MED-01, R-FIN-02).  
3. **Postponed** is appropriate when documentation or medical evidence is pending.  

## D — Escalation to Genie / structured data

Questions such as “What is the max sum assured for PRD-TERM-001 for age 40?” should be resolved against **ref_underwriting_limits** and **dim_product**, not free-text alone.

## E — Escalation to knowledge base

Questions about **definitions**, **nominee**, or **product positioning** should use the **product guide** and **manual excerpt** documents in the knowledge volume.
