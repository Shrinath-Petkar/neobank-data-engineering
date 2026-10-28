# 04_Email_Notification

This module sends an automated HTML email summary after the full pipeline run completes.

## Notebooks

### 01_Send_Email
1. Receives `run_id` as a widget parameter
2. Queries `banking.metadata.pipeline_runs` joined with `banking.metadata.tables` to get the execution audit for all tables in this run
3. Computes overall status (SUCCESS if all tables succeeded, FAILED otherwise)
4. Converts the audit DataFrame to an HTML table using pandas
5. Builds an HTML email body with the audit summary table
6. Retrieves the Gmail App Password from the `banking-scope` secret scope
7. Sends the email via Gmail SMTP (`smtp.gmail.com:587` with STARTTLS)

The email subject follows the format: `NeoBank | SUCCESS | End to End Run` or `NeoBank | FAILED | End to End Run`.

## Integration

This notebook is the final task in the **NeoBank_Master_Job**, executed after the Silver-to-Gold transformation completes.
