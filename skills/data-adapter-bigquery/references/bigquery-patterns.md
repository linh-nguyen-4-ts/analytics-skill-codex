# BigQuery Patterns

Use this file when profiling unfamiliar BigQuery datasets.

## Quick Discovery

```bash
python3 scripts/bq_adapter.py datasets
python3 scripts/bq_adapter.py tables dop
python3 scripts/bq_adapter.py schema dop.applications
python3 scripts/bq_adapter.py preview dop.applications --limit 5
```

## Profiling Queries

### Row count and freshness

```sql
SELECT
  COUNT(*) AS row_count,
  MAX(created_at) AS latest_created_at
FROM `project.dataset.table`;
```

### Distinct key versus raw row count

```sql
SELECT
  COUNT(*) AS row_count,
  COUNT(DISTINCT application_id) AS distinct_application_id
FROM `project.dataset.table`;
```

### Status distribution

```sql
SELECT
  status,
  COUNT(*) AS row_count,
  COUNT(DISTINCT application_id) AS distinct_application_id
FROM `project.dataset.table`
GROUP BY 1
ORDER BY row_count DESC;
```

### Join explosion check

```sql
WITH joined AS (
  SELECT
    a.application_id,
    b.service_name
  FROM `project.dataset.table_a` a
  LEFT JOIN `project.dataset.table_b` b
    ON a.application_id = b.application_id
)
SELECT
  COUNT(*) AS row_count,
  COUNT(DISTINCT application_id) AS distinct_application_id
FROM joined;
```

## JSON Patterns

- Use `JSON_VALUE(payload, '$.field')` for scalar strings or numbers.
- Use `JSON_QUERY(payload, '$.object')` for JSON fragments.
- Fall back to `REGEXP_EXTRACT` only when nested JSON is inconsistent or stored as escaped text.

## Partition Discipline

- Add partition filters early on large tables.
- Avoid trend conclusions from the current incomplete day unless the user asked for near-real-time data.
- Call out late-arriving data when the latest partition looks thin.

## Troubleshooting

- Run `gcloud auth application-default login` if the client cannot obtain credentials.
- Run `gcloud auth application-default set-quota-project <billing-project>` if jobs fail because of quota project issues.
- Distinguish the billing project from the data project in your notes.
