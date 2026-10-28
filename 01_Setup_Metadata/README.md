# 01_Setup_Metadata

This module sets up the foundational metadata framework that drives the entire pipeline. It creates the Unity Catalog structures and populates table definitions, load parameters, and watermark tracking.

## Notebooks

### 01_Setup_Metadata
Creates the `banking` catalog and three schemas (`metadata`, `source`, `bronze`), a source volume for blob file landing, and four metadata tables:

| Table | Purpose |
|-------|---------|
| `banking.metadata.tables` | Static table definitions — source system, schema, table name, bronze/silver/gold routing, active flag, load order |
| `banking.metadata.table_parameters` | Per-table load parameters — `load_type` (MERGE / APPEND / FULL), `primary_key`, `watermark_column` |
| `banking.metadata.table_watermarks` | Incremental load watermark tracking — `last_watermark_value`, `last_updated_at`, `last_run_id` |
| `banking.metadata.pipeline_runs` | Audit log for every pipeline execution — `run_id`, `table_id`, `layer`, `start_time`, `end_time`, `status`, `number_of_records`, `error_message` |

Also inserts metadata rows for 6 source tables (customers, accounts, transactions, branches, credit_bureau_reports, payment_gateway_logs) and 5 gold tables (customer_360, branch_performance, transaction_channel_summary, daily_bank_kpi, risk_customer_summary).

### 02_Check_Metadata
A verification notebook that queries all four metadata tables to confirm the setup was successful. Useful for debugging and validating metadata before running the pipeline.

## Source Table Registry

| ID | Table | Source | Load Type | Primary Key | Watermark |
|----|-------|--------|-----------|------------|-----------|
| 1 | customers | supabase | MERGE | customer_id | updated_at |
| 2 | accounts | supabase | MERGE | account_id | updated_at |
| 3 | transactions | supabase | APPEND | txn_id | txn_timestamp |
| 4 | branches | supabase | FULL | branch_code | — |
| 5 | credit_bureau_reports | blob | MERGE | customer_id | bureau_pull_date |
| 6 | payment_gateway_logs | blob | APPEND | txn_id | processed_timestamp |

## Gold Table Registry

| ID | Table | Description |
|----|-------|-------------|
| 7 | customer_360 | 360-degree customer view |
| 8 | branch_performance | Branch-level KPIs |
| 9 | transaction_channel_summary | Payment gateway analytics |
| 10 | daily_bank_kpi | Daily bank-wide metrics |
| 11 | risk_customer_summary | Credit risk aggregation |
