# Analytics Skill Codex

Codex skill bundle for data insight work on unfamiliar databases.

This repo packages three skills that work together:

- `data-insight-core`: database-agnostic workflow for intake, schema exploration, validation, and reporting
- `data-adapter-bigquery`: BigQuery adapter for access checks, schema discovery, previews, and SQL execution
- `product-context-template`: template for capturing product entities, lifecycle rules, KPI definitions, source-of-truth tables, and known data caveats

## Repo Structure

```text
skills/
  data-insight-core/
  data-adapter-bigquery/
  product-context-template/
```

## Install

Copy the skill folders into your Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/* "${CODEX_HOME:-$HOME/.codex}/skills/"
```

If you want to validate skills locally, install the helper dependencies:

```bash
python3 -m pip install --user -r requirements.txt
```

## New User Quickstart

1. Install the skills into `~/.codex/skills`.
2. If you will use BigQuery, configure the adapter:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/data-adapter-bigquery/scripts/bq_adapter.py" setup
python3 "${CODEX_HOME:-$HOME/.codex}/skills/data-adapter-bigquery/scripts/bq_adapter.py" test
```

3. Pick one real use case instead of trying to model the whole product at once.
   Example: approval funnel for the last 14 days.
4. Create a real product context by copying the template:

```bash
cp -R "${CODEX_HOME:-$HOME/.codex}/skills/product-context-template" \
  "${CODEX_HOME:-$HOME/.codex}/skills/dop-context"
```

5. Update the copied `SKILL.md` and fill the files under `references/`.
6. Confirm the draft context with a PO, analyst, or backend owner before treating it as source of truth.

## Recommended Workflow

Use the three skills together:

1. `$data-insight-core` to frame the business question and validation approach
2. `$data-adapter-bigquery` to inspect schema and query the data
3. Your copied product context skill such as `$dop-context` to define entities, lifecycle, KPI rules, and caveats

The key principle is:

`business questions + schema discovery + product context + validation checks -> trustworthy insight`

Do not rely on schema alone to infer business meaning. Confirm the parts that data cannot prove by itself:

- what entity should be counted
- what success and failure mean
- which table is source of truth
- what number should reconcile with an existing dashboard or report

## Example Prompts

Draft a new product context:

```text
Use $data-insight-core and $data-adapter-bigquery.
Interview me with only the minimum business questions, inspect the schema first, and draft a product context for DOP onboarding.
Mark every unclear item as Open Question.
```

Analyze a real metric:

```text
Use $data-insight-core, $data-adapter-bigquery, and $dop-context.
Analyze the DOP onboarding approval funnel for the last 14 days.
Validate the counting rule, state assumptions explicitly, and reconcile against any known source-of-truth number.
```

## Included Helpers

- `skills/data-adapter-bigquery/scripts/bq_adapter.py`: setup, access test, datasets, tables, schema, preview, query
- `skills/data-insight-core/scripts/render_report.py`: turn structured findings in JSON into a markdown report

## Local Validation

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/data-insight-core
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/data-adapter-bigquery
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/product-context-template
```

## Notes

- `data-adapter-bigquery` expects `google-cloud-bigquery`.
- `quick_validate.py` expects `PyYAML`.
- Do not commit local `.env` files with credentials.
