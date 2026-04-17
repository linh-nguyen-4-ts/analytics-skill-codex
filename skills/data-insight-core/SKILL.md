---
name: data-insight-core
description: Explore unfamiliar databases, align schema with business meaning, validate metrics with evidence, and produce trustworthy insight reports. Use when Codex needs to analyze a new database, map tables to product flows, confirm definitions with the user, or avoid unsupported assumptions in data analysis.
---

# Data Insight Core

Use this skill as the database-agnostic workflow layer for data analysis. Pair it with one database adapter skill and, when available, one product-context skill.

## Start Here

1. Read [intake-checklist.md](references/intake-checklist.md) to collect the minimum business context before querying.
2. Use a database adapter skill to inspect schema, preview data, and run queries.
3. Load a product-context skill if one exists for the domain you are analyzing.
4. Read [validation-checklist.md](references/validation-checklist.md) before presenting conclusions.
5. Use [report-template.md](references/report-template.md) or `scripts/render_report.py` to structure the final output.

## Workflow

### 1. Frame the analysis request

Ask only for the business facts that data cannot reveal reliably:

- business goal or decision to support
- time range
- target entity and counting rule
- success, failure, and in-progress definitions
- existing report, dashboard, or source of truth to reconcile against
- audience and expected output format

If information is missing but not blocking, proceed with a clearly labeled working assumption. Do not ask the user to restate metadata that can be discovered from the database.

### 2. Build database understanding first

Use the adapter to discover:

- schemas, datasets, tables, and views
- candidate primary keys and join keys
- table grain
- event timestamps and partitions
- status columns and enum values
- null rates, duplicate rates, and row counts
- example records for unfamiliar JSON or nested fields

Prefer a quick profiling pass before any complex funnel query.

### 3. Separate evidence from inference

Classify every important statement into one of these buckets:

- confirmed by user or product documentation
- observed directly in data
- inferred and still unvalidated

Do not present inferred business meaning as a fact. Convert uncertain mappings into validation questions or evidence queries.

### 4. Validate before concluding

Run the checks in [validation-checklist.md](references/validation-checklist.md). At minimum:

- compare `COUNT(*)` and `COUNT(DISTINCT key)`
- verify joins do not multiply rows unexpectedly
- confirm status mappings against actual values
- check time ordering for lifecycle steps
- test any source-of-truth claim against an existing report or operational number when possible
- note data freshness, late-arriving data, and backfills

When validation fails, report the conflict instead of forcing a neat answer.

### 5. Produce a decision-ready report

Lead with the smallest set of numbers and anomalies that help the audience act. Include:

- key highlights
- metric definitions
- evidence and query notes
- assumptions
- confidence level
- recommended next checks or actions

## Output Rules

- Show both absolute count and percentage for rate metrics.
- State the denominator explicitly.
- Name the table grain whenever a query spans multiple tables.
- Include at least one sentence on what is confirmed versus still assumed.
- If the result is unstable because of missing business definitions, say so.
- If the user asks for an insight report, keep the top summary short and move detail below it.

## Resource Guide

- Read [intake-checklist.md](references/intake-checklist.md) when opening a new analysis request.
- Read [validation-checklist.md](references/validation-checklist.md) before you trust a metric or funnel.
- Read [report-template.md](references/report-template.md) when writing the final answer.
- Use `scripts/render_report.py` when you already have structured findings and want a consistent markdown report quickly.
