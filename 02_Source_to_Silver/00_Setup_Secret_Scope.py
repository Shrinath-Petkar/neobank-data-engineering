# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# DBTITLE 1,Define Connection Variables
# =====================================================
# 1️⃣ Define Connection Variables (EDIT THESE)
# =====================================================

# Supabase PostgreSQL connection details
# Direct connection:  db.<project-ref>.supabase.co:5432
# Session pooler:     aws-0-<region>.pooler.supabase.com:5432
# Transaction pooler: aws-0-<region>.pooler.supabase.com:6543 (use 5432 for JDBC)
supabase_host = "<YOUR_SUPABASE_HOST>"
supabase_port = "5432"
supabase_database = "postgres"
supabase_user = "<YOUR_SUPABASE_USER>"
supabase_password = "<YOUR_SUPABASE_PASSWORD>"

# Secret scope name (will be created if not exists)
secret_scope_name = "banking-scope"

# Secret key name (single secret containing full JSON)
secret_key_name = "supabase-connection-json"
# secret_key_name = "sqlserver-connection-json-dummy"

# COMMAND ----------

# DBTITLE 1,Build JSON Object
# =====================================================
# 2️⃣ Build JSON Object
# =====================================================

import json

connection_config = {
    "host": supabase_host,
    "port": supabase_port,
    "database": supabase_database,
    "user": supabase_user,
    "password": supabase_password,
    "driver": "org.postgresql.Driver",
    "sslmode": "require"
}

connection_json = json.dumps(connection_config)

print("Generated JSON Configuration:")
print(connection_json)


# COMMAND ----------

# DBTITLE 1,Get Workspace Context
# Python cell in the same workspace notebook
ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()

api_url  = ctx.apiUrl().getOrElse(None)     # e.g. https://adb-...azuredatabricks.net
api_token = ctx.apiToken().getOrElse(None)  # personal access token for this session

print(api_url)  # api_token stays in memory only — never print or log it


import requests
import json

# ----------------------------------------
# Configuration
# ----------------------------------------
DATABRICKS_INSTANCE = api_url  # Replace with your workspace URL
DATABRICKS_TOKEN = api_token  # Replace with your PAT

scope_name = secret_scope_name  # Scope to be created
backend_type = "DATABRICKS"     # Use "AWS_SECRETSMANAGER" if integrating with AWS Secrets Manager

# COMMAND ----------



# ----------------------------------------
# API Endpoint
# ----------------------------------------
url = f"{DATABRICKS_INSTANCE}/api/2.0/secrets/scopes/create"

headers = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "scope": scope_name
}

# ----------------------------------------
# Send request
# ----------------------------------------
response = requests.post(url, headers=headers, data=json.dumps(payload))

# ----------------------------------------
# Handle response
# ----------------------------------------
if response.status_code == 200:
    print(f"Secret scope '{scope_name}' created successfully.")
else:
    print("Failed to create secret scope.")
    print("Status Code:", response.status_code)
    print("Response:", response.text)


# COMMAND ----------

import requests
import json

scope = secret_scope_name          # Already existing scope
secret_key = secret_key_name       # Name of the secret entry
secret_value = connection_json # Value to store securely

# -------------------------------------------------
# API Endpoint
# -------------------------------------------------
url = f"{DATABRICKS_INSTANCE}/api/2.0/secrets/put"

headers = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "scope": scope,
    "key": secret_key,
    "string_value": secret_value
}

# -------------------------------------------------
# Send Request
# -------------------------------------------------
response = requests.post(url, headers=headers, data=json.dumps(payload))

# -------------------------------------------------
# Output
# -------------------------------------------------
if response.status_code == 200:
    print(f"Secret '{secret_key}' created successfully in scope '{scope}'.")
else:
    print("Failed to create secret.")
    print("Status:", response.status_code)
    print("Response:", response.text)


# COMMAND ----------

# =====================================================
# 5️⃣ Verify Secret Retrieval
# =====================================================

try:
    retrieved_json = dbutils.secrets.get(
        scope=secret_scope_name,
        key=secret_key_name
    )
    
    print("Secret retrieved successfully.")
    
    parsed = json.loads(retrieved_json)
    print("Parsed JSON:")
    print(parsed)
    
except Exception as e:
    print("Secret verification failed:")
    print(str(e))


# COMMAND ----------

import requests
import json

scope = secret_scope_name          # Already existing scope
secret_key = 'gmail_api_key'       # Name of the secret entry
secret_value = '<YOUR_GMAIL_APP_PASSWORD>' # Value to store securely

# -------------------------------------------------
# API Endpoint
# -------------------------------------------------
url = f"{DATABRICKS_INSTANCE}/api/2.0/secrets/put"

headers = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "scope": scope,
    "key": secret_key,
    "string_value": secret_value
}

# -------------------------------------------------
# Send Request
# -------------------------------------------------
response = requests.post(url, headers=headers, data=json.dumps(payload))

# -------------------------------------------------
# Output
# -------------------------------------------------
if response.status_code == 200:
    print(f"Secret '{secret_key}' created successfully in scope '{scope}'.")
else:
    print("Failed to create secret.")
    print("Status:", response.status_code)
    print("Response:", response.text)