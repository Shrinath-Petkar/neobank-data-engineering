# 03_Silver_to_Gold

This module transforms Silver-layer data into business-ready Gold tables. A driver notebook orchestrates individual transformation notebooks, each creating an analytical table in `banking.gold`.

## Notebooks

### 01_Silver_to_Gold_Driver
The orchestration notebook that:
1. Receives `run_id` and `table_metadata` (table_id + table_name) as widgets
2. Creates an audit entry in `pipeline_runs` with status `INPROGRESS`
3. Dynamically calls the appropriate gold transformation notebook via `dbutils.notebook.run()`
4. Captures the record count returned by the child notebook
5. Updates the audit entry with final status, record count, and error message
6. Raises an exception if the child notebook fails

### gold_transformations/
Contains individual transformation notebooks — see [gold_transformations/README.md](gold_transformations/README.md) for details.

## Job Orchestration

The **NeoBank_Silver_to_Gold** job calls `01_Read_Tables_List` (reused from Source_to_Silver), then uses a For Each task (concurrency 4) to call `01_Silver_to_Gold_Driver` for each gold table.

## Audit Flow

```
pipeline_runs INSERT (INPROGRESS)
      ↓
dbutils.notebook.run(gold_transformations/{table_name})
      ↓
pipeline_runs UPDATE (SUCCESS / FAILED + record_count + error_message)
```
