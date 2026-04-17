---
name: data-adapter-bigquery
description: Connect to BigQuery, verify access, inspect datasets and tables, preview rows, and run analysis SQL safely. Use when Codex needs a BigQuery adapter for schema discovery, data profiling, or evidence-based metrics work.
---

# Data Adapter Bigquery

Use this skill as the BigQuery-specific execution layer for a broader data analysis workflow.

## Start Here

1. Configure credentials with `scripts/bq_adapter.py setup` or by writing a `.env` file next to the script.
2. Verify connectivity with `scripts/bq_adapter.py test`.
3. Inspect datasets, tables, schema, and preview rows before writing analysis queries.
4. Read [bigquery-patterns.md](references/bigquery-patterns.md) when working with JSON, partitions, or profiling queries.

## Workflow

### 1. Configure access

Support either `gcloud` user credentials or ADC or a service account file. Keep these values in `.env`:

- `GCP_BILLING_PROJECT`
- `GCP_DATA_PROJECT`
- `GOOGLE_APPLICATION_CREDENTIALS`

Always run a cheap connectivity test before analysis.

### 2. Discover before querying

Use these commands first:

- `scripts/bq_adapter.py datasets`
- `scripts/bq_adapter.py tables <dataset>`
- `scripts/bq_adapter.py schema <dataset.table>`
- `scripts/bq_adapter.py preview <dataset.table> --limit 5`

Do not write a funnel or KPI query until you know the table grain, timestamp fields, and status columns.

### 3. Query carefully

- Prefer `COUNT(DISTINCT business_key)` unless the user explicitly wants event counts.
- Add time filters early, especially on partitioned tables.
- Limit exploratory output.
- Stage complex logic with CTEs.
- Extract JSON scalars with `JSON_VALUE` and JSON objects with `JSON_QUERY` or `JSON_EXTRACT`.

### 4. Troubleshoot access or cost issues

If a query fails, check:

- whether the billing project can run jobs
- whether the data project contains the referenced dataset
- whether `gcloud auth application-default login` is needed
- whether the quota project is missing
- whether the SQL uses the correct project-qualified table names

## Output Rules

- Report which project ran the job and which project stored the data when they differ.
- Mention any table qualification or JSON extraction assumptions.
- Keep sample queries small and safe during exploration.

## Resource Guide

- Use `scripts/bq_adapter.py` for setup, connectivity tests, schema discovery, previews, and queries.
- Read [bigquery-patterns.md](references/bigquery-patterns.md) for query patterns and troubleshooting notes.
