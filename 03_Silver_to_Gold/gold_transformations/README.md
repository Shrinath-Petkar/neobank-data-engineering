# gold_transformations

This subfolder contains the individual SQL transformation notebooks that create Gold-layer analytical tables. Each notebook is called dynamically by `01_Silver_to_Gold_Driver` and returns the row count of the resulting table via `dbutils.notebook.exit()`.

## Transformations

### customer_360
A 360-degree customer view combining customers, accounts, transactions, branches, and credit bureau data. Includes account aggregations (total accounts, total balance), transaction aggregations (total transactions, total amount), latest credit score and risk grade, and a customer segment classification (HIGH_VALUE / MEDIUM_VALUE / LOW_VALUE based on total balance).

| Column | Description |
|--------|-------------|
| customer_id | Primary key |
| customer_name | First + last name |
| branch_name | Customer's branch |
| total_accounts | Count of accounts |
| total_balance | Sum of account balances |
| total_transactions | Count of transactions |
| total_transaction_amount | Sum of transaction amounts |
| credit_score | Latest credit score |
| risk_grade | Credit risk grade |
| external_active_loans | Active external loans |
| external_overdue_amount | Overdue amount |
| customer_segment | HIGH_VALUE / MEDIUM_VALUE / LOW_VALUE |

### branch_performance
Branch-level performance aggregation with total customers, accounts, deposits, transactions, and transaction amounts per branch.

### daily_bank_kpi
Daily bank-wide KPIs including total customers, accounts, balance, transactions, transaction amount, average credit score, and high-risk customer count — cross-joined with daily transaction aggregates.

### risk_customer_summary
Credit risk aggregation by risk grade — total customers, average credit score, total external loans, and total overdue amount.

### transaction_channel_summary
Payment gateway analytics — total, successful, and failed transactions per gateway/device/date combination, with average processing time.
