# PostgreSQL Patterns

Use this file when analyzing PostgreSQL tables through the adapter.

## Quick Discovery

```bash
python3 scripts/postgres_adapter.py test
python3 scripts/postgres_adapter.py schemas
python3 scripts/postgres_adapter.py tables public
python3 scripts/postgres_adapter.py describe public.orders
python3 scripts/postgres_adapter.py preview public.orders --limit 5
python3 scripts/postgres_adapter.py profile public.orders
```

## SQL Pattern

The adapter accepts arbitrary read-only SQL for `query`:

```bash
python3 scripts/postgres_adapter.py query \
  "SELECT status, COUNT(*) AS row_count FROM public.orders GROUP BY 1 ORDER BY row_count DESC"
```

You may also provide a `.sql` file:

```bash
python3 scripts/postgres_adapter.py query --file ./query.sql
```

## Recommended Checks

### Row count versus distinct entity count

```sql
SELECT
  COUNT(*) AS row_count,
  COUNT(DISTINCT application_id) AS distinct_application_id
FROM public.applications;
```

### Duplicate key check

```sql
SELECT
  application_id,
  COUNT(*) AS duplicate_rows
FROM public.application_events
GROUP BY 1
HAVING COUNT(*) > 1
ORDER BY duplicate_rows DESC
LIMIT 20;
```

### Soft-delete check

```sql
SELECT
  COUNT(*) AS deleted_rows
FROM public.orders
WHERE deleted_at IS NOT NULL;
```

## Common Caveats

- replicas may lag behind the primary database
- `timestamp without time zone` can silently shift daily metrics
- views can hide filters or deduplication logic
- audit tables and history tables can look like current-state tables
- exact `COUNT(DISTINCT)` on very large tables can be expensive

## Troubleshooting

- Prefer a read-only user.
- If a connection fails, check `DATABASE_URL`, host, port, SSL mode, and network access.
- If a table is not found, verify both the schema name and the search path.
- If profiling is too slow, start with `preview` and targeted aggregate queries before full profiling.
