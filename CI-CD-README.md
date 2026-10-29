# CI/CD Setup Guide

This project uses **Declarative Automation Bundles (DABs)** for infrastructure-as-code and **GitHub Actions** for automated deployment to Databricks.

---

## 📐 How It Works

```
Developer pushes to main ──► GitHub Actions ──► bundle validate ──► deploy to dev
Create tag v1.0.0       ──► GitHub Actions ──► bundle validate ──► deploy to prod
Pull request            ──► GitHub Actions ──► bundle validate (no deploy)
```

### Environments

| Target | Mode | Trigger | Description |
|--------|------|---------|-------------|
| `dev` | development | Push to `main` | Jobs prefixed with `[dev]`, user-scoped workspace paths |
| `prod` | production | Git tag `v*` | Shared workspace paths, no prefix |

---

## 📁 CI/CD File Structure

```
neobank-data-engineering/
├── databricks.yml                              # Main bundle config (variables, targets)
├── resources/
│   ├── neobank_master_job.job.yml              # Master orchestrator job
│   ├── neobank_source_to_silver_outer.job.yml  # Outer ingestion job
│   ├── neobank_source_to_silver_inner.job.yml  # Inner per-table job
│   ├── neobank_silver_to_gold.job.yml          # Gold transformation job
│   └── neobank_dashboard.dashboard.yml         # NeoBank Lakeview dashboard
├── dashboards/
│   └── neobank_dashboard.lvdash.json           # Dashboard serialized JSON
├── .github/workflows/
│   └── deploy.yml                              # GitHub Actions CI/CD workflow
└── CI-CD-README.md                             # This file
```

---

## 🔑 Required GitHub Secrets

Add these as repository secrets in **Settings > Secrets and variables > Actions**:

| Secret Name | Value |
|-------------|-------|
| `DATABRICKS_HOST` | Your Databricks workspace URL (e.g., `https://dbc-xxx.cloud.databricks.com`) |
| `DATABRICKS_TOKEN` | A Databricks Personal Access Token (PAT) |

### How to Get These Values

1. **DATABRICKS_HOST**: Copy your workspace URL from the browser address bar
2. **DATABRICKS_TOKEN**: In Databricks, go to **Settings > Developer > Access tokens > Generate new token**

### Adding Secrets to GitHub

1. Go to your repo: https://github.com/Shrinath-Petkar/neobank-data-engineering
2. **Settings > Secrets and variables > Actions > New repository secret**
3. Add `DATABRICKS_HOST` and `DATABRICKS_TOKEN`

---

## 🚀 Deployment Commands

### Local Development (from the bundle root)

```bash
# Validate the bundle
databricks bundle validate --target dev

# Deploy to dev
databricks bundle deploy --target dev

# Deploy to prod (requires tag)
databricks bundle deploy --target prod

# Run the master job
databricks bundle run neobank_master_job --target dev
```

### Automated via GitHub Actions

| Action | Result |
|--------|--------|
| Push to `main` | Validates and deploys to `dev` |
| Create tag `v1.0.0` | Validates and deploys to `prod` |
| Open PR to `main` | Validates only (no deploy) |

### Creating a Production Release

```bash
git tag v1.0.0
git push origin v1.0.0
```
This triggers the `deploy-prod` job in GitHub Actions.

---

## 📦 Bundle Resources

The bundle defines 4 Databricks Jobs and 1 Dashboard:

| Resource Key | Job/Dashboard Name | Description |
|-------------|----------|-------------|
| `neobank_master_job` | NeoBank_Master_Job | Top-level orchestrator |
| `neobank_source_to_silver_outer` | NeoBank_Source_to_Silver_Outer | Reads table list, fans out via For Each |
| `neobank_source_to_silver_inner` | NeoBank_Source_to_Silver_Inner | Per-table: parameters → bronze → silver |
| `neobank_silver_to_gold` | NeoBank_Silver_to_Gold | Reads gold table list, fans out gold driver |
| `neobank_dashboard` | NeoBank_Dashboard | Lakeview dashboard on banking.gold (4 pages, 12 datasets) |

### Cross-Job References

The Master job references other jobs using DABs resource IDs:
```yaml
run_job_task:
  job_id: ${resources.jobs.neobank_source_to_silver_outer.id}
```

This ensures the correct job ID is resolved automatically during deployment.

---

## 🔧 Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `catalog` | `banking` | Unity Catalog name |
| `warehouse_id` | `f0bff84206d339e1` | SQL Warehouse for dashboard refresh |
| `run_id` | `123456` | Default pipeline run ID for audit tracking |

Override variables per environment in the `targets` section of `databricks.yml`.

---

## ⚠️ Notes

- The `00_Setup_Secret_Scope` notebook must be run manually before the first pipeline run — it creates the Databricks secret scope.
- In `dev` mode, job names are prefixed with `[dev <username>]` and deployed to user-specific workspace paths.
- In `prod` mode, jobs are deployed to shared workspace paths with no prefix.
- The NeoBank dashboard is included as a `dashboards` resource (`neobank_dashboard.dashboard.yml`) and refreshed automatically by the Master job's `Refresh_Dashboard` task after the Silver-to-Gold step completes.
