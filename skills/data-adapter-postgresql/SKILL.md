---
name: data-adapter-postgresql
description: Connect to PostgreSQL, verify access, inspect schemas and tables, preview rows, profile tables, and run analysis SQL safely. Use when Codex needs a PostgreSQL adapter for operational databases, analytics replicas, or evidence-based metrics work.
---

# Data Adapter Postgresql

Use this skill as the PostgreSQL-specific execution layer for a broader data analysis workflow.

## Start Here

1. Configure credentials with `scripts/postgres_adapter.py setup` or by writing a `.env` file next to the script.
2. Verify connectivity with `scripts/postgres_adapter.py test`.
3. Inspect schemas, tables, columns, and preview rows before writing analysis queries.
4. Read [postgresql-patterns.md](references/postgresql-patterns.md) for query patterns, caveats, and troubleshooting notes.

## Workflow

### 1. Configure access

Support either a full `DATABASE_URL` or discrete PostgreSQL environment variables in `.env`:

- `DATABASE_URL`
- `PGHOST`
- `PGPORT`
- `PGDATABASE`
- `PGUSER`
- `PGPASSWORD`
- `PGSSLMODE`
- `PGSCHEMA`

Treat the account as read-only. Always run a cheap connectivity test before analysis.

### 2. Discover before querying

Use these commands first:

- `scripts/postgres_adapter.py schemas`
- `scripts/postgres_adapter.py tables <schema>`
- `scripts/postgres_adapter.py describe <schema.table>`
- `scripts/postgres_adapter.py preview <schema.table> --limit 5`
- `scripts/postgres_adapter.py profile <schema.table>`

Do not write a funnel or KPI query until you know the table grain, timestamp fields, status columns, and whether the table is current-state or event history.

### 3. Query carefully

- Prefer `COUNT(DISTINCT business_key)` unless the user explicitly wants event counts.
- Use a schema-qualified table name when there is any ambiguity.
- Watch for soft-delete columns, history tables, and audit logs that can distort grain.
- Validate timezone assumptions before calculating day-level metrics.
- Limit exploratory output and use CTEs for complex logic.

### 4. Handle PostgreSQL caveats explicitly

When a result looks surprising, check:

- whether a view or materialized view differs from the base table
- whether `updated_at` is more reliable than `created_at` for freshness
- whether logical deletes are present
- whether the same business entity appears in both current and history tables
- whether joins multiply rows because of one-to-many relationships

## Output Rules

- Name the exact database and schema used.
- Mention any search-path, timezone, or read-replica assumptions.
- Show both row-level and entity-level counts when duplication is plausible.
- Keep previews and ad hoc queries small and safe during exploration.

## Resource Guide

- Use `scripts/postgres_adapter.py` for setup, connectivity tests, schema discovery, previews, profiling, and SQL queries.
- Read [postgresql-patterns.md](references/postgresql-patterns.md) for profiling and troubleshooting guidance.
