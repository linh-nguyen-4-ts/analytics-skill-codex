---
name: product-context-template
description: Capture product-specific entities, lifecycles, KPI definitions, source-of-truth tables, and known data caveats for use by data analysis skills. Use when onboarding a new product, database, or reporting domain before trusting derived insights.
---

# Product Context Template

Use this template to create a real product-context skill for one domain. Copy the folder, rename it to the product or business flow, then replace all placeholders in the reference files.

## Start Here

1. Create a product-specific copy of this template.
2. Fill in every reference file under `references/`.
3. Confirm the contents with a PO, analyst, or engineering owner.
4. Keep definitions versioned as the product changes.

## Required References

- [entities.md](references/entities.md): core business entities and join keys
- [lifecycle.md](references/lifecycle.md): status and stage transitions
- [metrics.md](references/metrics.md): KPI definitions and counting rules
- [source-of-truth.md](references/source-of-truth.md): authoritative tables, reports, and exceptions
- [known-data-issues.md](references/known-data-issues.md): caveats, bugs, and reconciliation notes

## Authoring Rules

- Prefer concrete definitions over prose.
- Record exact status values, table names, and keys whenever known.
- Mark each unclear rule as `Open Question` until it is confirmed.
- Keep old definitions with dates if business meaning changed over time.

## Usage Rules

- Load this skill together with a database adapter and `data-insight-core`.
- Treat missing references as a signal that conclusions should stay provisional.
- Keep the reference files short enough to scan, but rich enough to remove ambiguity.
