---
name: data-adapter-local-tabular
description: Inspect and query local CSV and XLSX files safely with schema discovery, previews, profiling, and SQL analysis. Use when Codex needs a local-file adapter for spreadsheet data, flat files, or ad hoc analytics on tabular exports.
---

# Data Adapter Local Tabular

Use this skill as the local-file execution layer for CSV and XLSX analysis.

## Start Here

1. Point the adapter at a local source path such as `report.csv` or `workbook.xlsx#Sheet1`.
2. Run `inspect` before analysis to see file type, sheets, and inferred columns.
3. Run `preview` or `profile` before writing any metric query.
4. Read [local-tabular-patterns.md](references/local-tabular-patterns.md) when handling messy spreadsheets or mixed-type columns.

## Workflow

### 1. Identify the source correctly

Accepted source formats:

- `path/to/file.csv`
- `path/to/file.xlsx`
- `path/to/file.xlsx#Sheet Name`

If an XLSX source omits the sheet name, inspect it first and choose the relevant sheet explicitly for analysis.

### 2. Discover before querying

Use these commands first:

- `scripts/local_tabular_adapter.py inspect <source>`
- `scripts/local_tabular_adapter.py describe <source>`
- `scripts/local_tabular_adapter.py preview <source> --limit 5`
- `scripts/local_tabular_adapter.py profile <source>`

Do not trust spreadsheet headers or types until the preview confirms them.

### 3. Query carefully

- Use `source_data` as the default table name in ad hoc SQL.
- Prefer `COUNT(DISTINCT business_key)` for entity metrics.
- Check whether the first row is truly the header before analyzing an XLSX file.
- Watch for duplicated, blank, or merged headers in exported spreadsheets.
- Validate date and numeric columns because local files often mix strings with real typed values.

### 4. Handle spreadsheet caveats explicitly

For XLSX files, assume the data may contain:

- multiple sheets with different semantics
- decorative top rows before the real header
- merged cells and blank header names
- formulas where the displayed value matters more than the formula text
- mixed types in the same column

If the workbook is messy, call out the limitation and keep conclusions provisional.

## Output Rules

- Name the exact file and sheet you analyzed.
- Mention header or type-normalization assumptions.
- Show both row-level and entity-level counts when duplication is plausible.
- Keep exploratory previews small and safe.

## Resource Guide

- Use `scripts/local_tabular_adapter.py` for inspection, schema discovery, profiling, previews, and SQL queries.
- Read [local-tabular-patterns.md](references/local-tabular-patterns.md) for recommended commands and caveats.
