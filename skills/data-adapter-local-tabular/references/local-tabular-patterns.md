# Local Tabular Patterns

Use this file when analyzing CSV or XLSX data on disk.

## Quick Discovery

```bash
python3 scripts/local_tabular_adapter.py inspect ./report.csv
python3 scripts/local_tabular_adapter.py inspect './workbook.xlsx#Sheet1'
python3 scripts/local_tabular_adapter.py describe ./report.csv
python3 scripts/local_tabular_adapter.py preview ./report.csv --limit 5
python3 scripts/local_tabular_adapter.py profile './workbook.xlsx#Sheet1'
```

## SQL Pattern

The adapter exposes the selected file or sheet as `source_data`.

```bash
python3 scripts/local_tabular_adapter.py query ./report.csv \
  "SELECT status, COUNT(*) AS row_count FROM source_data GROUP BY 1 ORDER BY row_count DESC"
```

You may also use `{table}` as a placeholder, and the adapter will replace it with `source_data`.

## When the Source Is XLSX

- Inspect the workbook first to see sheet names.
- Prefer an explicit sheet reference such as `file.xlsx#Raw Data`.
- Verify the inferred header row before running business metrics.
- Expect mixed types and blank cells.

## Recommended Checks

### Row count and distinct entity count

```sql
SELECT
  COUNT(*) AS row_count,
  COUNT(DISTINCT application_id) AS distinct_application_id
FROM source_data;
```

### Duplicate key check

```sql
SELECT
  application_id,
  COUNT(*) AS duplicate_rows
FROM source_data
GROUP BY 1
HAVING COUNT(*) > 1
ORDER BY duplicate_rows DESC
LIMIT 20;
```

### Null-rate sanity check

Use `profile` first. It calculates row count, null count, distinct count, and a small sample for each column.

## Caveats

- Decorative title rows can be misread as headers.
- Formula cells are read as displayed values, not formulas.
- Exported numbers may arrive as strings with commas or currency symbols.
- Large workbooks may be slower because XLSX sheets are normalized through a temporary CSV before query execution.
