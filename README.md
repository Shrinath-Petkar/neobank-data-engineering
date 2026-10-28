# NeoBank — End-to-End Banking Data Engineering Pipeline

An end-to-end banking data engineering project built on **Databricks** using a **medallion architecture** (Bronze → Silver → Gold). The pipeline ingests data from multiple source systems (Supabase PostgreSQL and Blob storage), transforms it through incremental loads with watermark tracking, builds analytical Gold tables, powers an executive dashboard, and sends automated email notifications — all orchestrated by Databricks Jobs.

---

## 🏗️ Architecture Overview

```
                    ┌─────────────────┐     ┌─────────────────┐
                    │   Supabase PG   │     │  Blob Storage   │
                    │  (JDBC / 4 tbl) │     │  (Auto Loader)  │
                    └────────┬────────┘     └────────┬────────┘
                             │                       │
                             ▼                       ▼
                    ┌─────────────────────────────────────┐
                    │           BRONZE LAYER               │
                    │   Raw ingest with audit columns      │
                    └────────────────┬────────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────────┐
                    │           SILVER LAYER               │
                    │  MERGE / APPEND / FULL loads         │
                    │  Watermark-based incremental        │
                    └────────────────┬────────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────────┐
                    │            GOLD LAYER                │
                    │  customer_360, branch_performance,  │
                    │  daily_bank_kpi, risk_summary,      │
                    │  transaction_channel_summary        │
                    └────────────────┬────────────────────┘
                                     │
                        ┌────────────┴────────────┐
                        ▼                         ▼
              ┌──────────────┐         ┌──────────────────┐
              │  Dashboard   │         │  Email Notification│
              │  (4 pages)  │         │  (HTML via SMTP)  │
              └──────────────┘         └──────────────────┘
```

---

## 📁 Project Structure

```
neobank-data-engineering/
├── 01_Setup_Metadata/
│   ├── 01_Setup_Metadata.py      # Create catalog, schemas, metadata tables
│   ├── 02_Check_Metadata.sql      # Verify metadata setup
│   └── README.md
├── 02_Source_to_Silver/
│   ├── 00_Setup_Secret_Scope.py  # Create Databricks secret scope
│   ├── 01_Read_Tables_List.py    # Read table list from metadata
│   ├── 02_Read_Table_Parameters.py # Read load parameters per table
│   ├── 03_Source_to_Bronze.py    # Ingest from source to bronze
│   ├── 04_Bronze_to_Silver.py    # Transform bronze to silver
│   └── README.md
├── 03_Silver_to_Gold/
│   ├── 01_Silver_to_Gold_Driver.py # Orchestrate gold transformations
│   ├── gold_transformations/
│   │   ├── customer_360.sql          # 360-degree customer view
│   │   ├── branch_performance.sql    # Branch KPIs
│   │   ├── daily_bank_kpi.sql        # Daily bank-wide metrics
│   │   ├── risk_customer_summary.sql # Credit risk aggregation
│   │   ├── transaction_channel_summary.sql # Gateway analytics
│   │   └── README.md
│   └── README.md
├── 04_Email_Notification/
│   ├── 01_Send_Email.py          # HTML email with pipeline audit
│   └── README.md
├── .gitignore
└── README.md
```

---

## 📊 Data Sources

| Source | Tables | Connection Method |
|--------|--------|-------------------|
| Supabase PostgreSQL | customers, accounts, transactions, branches | JDBC (`jdbc:postgresql://`) |
| Blob / Volume (CSV) | credit_bureau_reports, payment_gateway_logs | Databricks Auto Loader (`cloudFiles`) |

---

## 🗄️ Data Layers (Medallion Architecture)

### Bronze Layer (`banking.bronze`)
Raw ingestion with audit columns. Both batch (JDBC) and streaming (Auto Loader) ingestion are supported. Schema is inferred on first load.

### Silver Layer (`banking.silver`)
Cleaned and conformed data with three load strategies:

| Load Type | Behavior | Used By |
|-----------|----------|---------|
| **MERGE** | Delta MERGE (upsert) on primary key | customers, accounts, credit_bureau_reports |
| **APPEND** | Append new records filtered by watermark | transactions, payment_gateway_logs |
| **FULL** | Overwrite entire table | branches |

### Gold Layer (`banking.gold`)
Business-ready analytical tables powering the dashboard:

| Table | Records | Description |
|-------|---------|-------------|
| `customer_360` | 4,000 | 360-degree customer view with accounts, transactions, credit, and segmentation |
| `branch_performance` | 4 | Branch-level deposits, customers, transactions |
| `transaction_channel_summary` | 5,716 | Gateway success/failure analytics by device and date |
| `daily_bank_kpi` | 396 | Daily bank-wide KPIs (customers, accounts, balance, risk) |
| `risk_customer_summary` | 3 | Credit risk aggregation by grade |

---

## 🔧 Metadata Framework

A metadata-driven design where table definitions, load parameters, watermarks, and audit logs are all stored in Unity Catalog:

| Table | Purpose |
|-------|---------|
| `banking.metadata.tables` | Table registry — source system, routing, active flag, load order |
| `banking.metadata.table_parameters` | Load config — load_type, primary_key, watermark_column |
| `banking.metadata.table_watermarks` | Incremental load tracking — last watermark value per table |
| `banking.metadata.pipeline_runs` | Full audit log — run_id, table_id, layer, status, records, errors |

---

## ⚙️ Job Orchestration

Four Databricks Jobs orchestrate the pipeline:

### 1. NeoBank_Master_Job
The top-level orchestrator that runs the entire pipeline end-to-end:

```
Source_to_Silver_BLOB ──┐
                        ├──► Silver_to_Gold ──► Send_Email
Source_to_Silver_SUPABASE┘                    └─► Dashboard Refresh
```

### 2. NeoBank_Source_to_Silver_Outer
Reads the table list from metadata, then fans out to the inner job using a **For Each** task (concurrency 4) for parallel table ingestion.

### 3. NeoBank_Source_to_Silver_Inner
Per-table sequential pipeline: `Read Parameters` → `Source to Bronze` → `Bronze to Silver`

### 4. NeoBank_Silver_to_Gold
Reads the gold table list, then fans out to the gold driver using a **For Each** task (concurrency 4) for parallel gold transformations.

---

## 📈 Dashboard

The **NeoBank Dashboard** is an AI/BI Lakeview dashboard with 4 pages:

### Executive Dashboard
- Total Customers (counter)
- Total Deposits (counter)
- Total Transactions (counter)
- High Risk Customers (counter)

### Customer Insights
- Customer Segment Distribution (bar chart)
- Credit Risk Distribution (pie chart)
- Top 10 Customers by Balance (table)

### Branch Performance
- Branch Deposits (pie chart)
- Branch Customers (pie chart)
- Branch Transaction Amount (bar chart)

### Channel Performance
- Gateway Success vs Failures (bar chart)
- Device Transaction Distribution (pie chart)

---

## 🚀 Key Features

- **Metadata-driven pipeline** — table definitions, load types, and watermarks stored in Unity Catalog, no hardcoded table lists
- **Multi-source ingestion** — JDBC (Supabase PostgreSQL) and Auto Loader (blob CSV) with unified metadata framework
- **Incremental loading** — watermark-based CDC with MERGE / APPEND / FULL strategies per table
- **Parallel processing** — Databricks For Each tasks with concurrency 4 for both ingestion and gold transformations
- **Full audit trail** — every table load tracked in `pipeline_runs` with status, timing, record count, and error message
- **Automated email notifications** — HTML email summary sent via Gmail SMTP after each run
- **Executive dashboard** — 4-page AI/BI Lakeview dashboard refreshed automatically by the master job
- **Secret management** — credentials stored in Databricks Secret Scope, not in code

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Platform | Databricks (Serverless Compute) |
| Storage | Unity Catalog (Delta Lake) |
| Source 1 | Supabase PostgreSQL (JDBC) |
| Source 2 | Databricks Volumes (CSV via Auto Loader) |
| Orchestration | Databricks Jobs (multi-task, For Each) |
| Dashboard | AI/BI Lakeview |
| Email | Gmail SMTP (Python `smtplib`) |
| Secrets | Databricks Secret Scope API |

---

## 🔧 Setup Instructions

### Prerequisites
- Databricks workspace with serverless compute enabled
- Unity Catalog enabled
- A Supabase PostgreSQL database with banking source tables (customers, accounts, transactions, branches)
- CSV files for credit_bureau_reports and payment_gateway_logs
- A Gmail App Password for email notifications

### Steps

1. **Clone this repo** into your Databricks workspace as a Git folder

2. **Run `01_Setup_Metadata/01_Setup_Metadata`** — Creates the `banking` catalog, schemas, volume, and all metadata tables

3. **Run `02_Source_to_Silver/00_Setup_Secret_Scope`** — Creates the `banking-scope` secret scope and stores your connection credentials. **Replace the placeholder values with your actual credentials before running.**

4. **Place CSV files** in `/Volumes/banking/source/volume/credit_bureau_reports/` and `/Volumes/banking/source/volume/payment_gateway_logs/`

5. **Run the NeoBank_Master_Job** — or run individual modules in order:
   - `02_Source_to_Silver` (for both `blob` and `supabase` source systems)
   - `03_Silver_to_Gold`
   - `04_Email_Notification`

6. **View the NeoBank Dashboard** for analytics

---

## ⚠️ Security Notes

- The `00_Setup_Secret_Scope` notebook contains **placeholder credentials** — replace with your own before running
- Never commit real passwords, API keys, or connection strings to version control
- The `.gitignore` file excludes `.env`, `.key`, and `secrets/` directories
- In production, use Databricks Secret Scope with Azure Key Vault or AWS Secrets Manager backend

---

## 📧 Contact

**Shrinath Petkar** — [GitHub](https://github.com/Shrinath-Petkar)

---

## 📄 License

This project is for portfolio/educational purposes.
