# 02_Source_to_Silver

This module handles data ingestion from external sources into the Bronze layer, followed by transformation into the Silver layer. It supports two source systems: **Supabase PostgreSQL** (JDBC) and **Blob storage** (Auto Loader for CSV files).

## Notebooks

### 00_Setup_Secret_Scope
Creates a Databricks secret scope (`banking-scope`) and stores two secrets:
- `supabase-connection-json` — JDBC connection details (host, port, database, user, password, driver, sslmode) as a single JSON string
- `gmail_api_key` — Gmail App Password for email notifications

> ⚠️ **Security Note:** This notebook has been sanitized — replace placeholder values with your actual credentials before running. Never commit real secrets to version control.

### 01_Read_Tables_List
Reads `banking.metadata.tables` filtered by `source_system` and `active_flag = true`, ordered by `load_order`. Returns the full table metadata as a list of dictionaries via `dbutils.jobs.taskValues.set()`, which the parent job passes to a For Each task for parallel processing.

### 02_Read_Table_Parameters
Receives a single table's metadata, reads its load parameters from `banking.metadata.table_parameters` (load_type, primary_key, watermark_column), and returns them as a JSON dictionary via task values.

### 03_Source_to_Bronze
The core ingestion notebook. Reads source data and writes to the Bronze layer:

- **Supabase (JDBC):** Reads the connection secret, builds a JDBC URL, and uses `spark.read.jdbc()` with watermark-based incremental filtering
- **Blob (Auto Loader):** Uses `cloudFiles` format with CSV schema inference and schema location tracking

Adds audit columns (`__ingested_at`), creates the bronze schema if needed, and writes as Delta tables. Records the run in `pipeline_runs` with status `INPROGRESS`.

### 04_Bronze_to_Silver
Transforms Bronze data into the Silver layer with three load strategies:

| Load Type | Behavior |
|-----------|----------|
| **FULL** | Overwrites the silver table entirely |
| **APPEND** | Appends new records (filtered by watermark) |
| **MERGE** | Upserts using Delta MERGE on primary key |

Updates the watermark in `table_watermarks` after successful load, and updates the audit entry in `pipeline_runs` with final status, record count, and error message.

## Job Orchestration

This module is orchestrated by two Databricks Jobs:

1. **NeoBank_Source_to_Silver_Outer** — Calls `01_Read_Tables_List`, then uses a For Each task (concurrency 4) to call the inner job for each table
2. **NeoBank_Source_to_Silver_Inner** — Calls `02_Read_Table_Parameters` → `03_Source_to_Bronze` → `04_Bronze_to_Silver` sequentially per table
