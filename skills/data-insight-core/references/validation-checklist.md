# Validation Checklist

Run these checks before presenting insights as trustworthy.

## 1. Counting Semantics

- Compare `COUNT(*)` with `COUNT(DISTINCT business_key)`.
- Check for deduplication rules such as retries, replays, resubmissions, or snapshots.
- Confirm whether the table stores events, current state, or one row per entity.

## 2. Join Integrity

- Verify join cardinality before using multi-table funnels.
- Count duplicated business keys after each join.
- Prefer staging CTEs that enforce one row per entity before aggregation.

## 3. Lifecycle Integrity

- Confirm timestamps appear in a valid order.
- Check whether some stages can repeat.
- Separate missing steps from delayed steps.

## 4. Status Meaning

- List actual status values from data.
- Confirm which values map to success, failure, cancel, timeout, or pending.
- Avoid collapsing technical statuses into business outcomes without confirmation.

## 5. Source-of-Truth

- Identify which table the business trusts for each KPI.
- If multiple candidate tables exist, compare counts and explain the difference.
- Reconcile with an existing dashboard or operational number whenever possible.

## 6. Freshness and Completeness

- Check max timestamp or latest partition.
- Note delayed ingestion, late-arriving events, and backfills.
- Avoid drawing trend conclusions from incomplete periods.

## 7. Edge Cases

- Anonymized or null user IDs
- Multiple products sharing one table
- Historical rows mixed with current rows
- Soft deletes or tombstones
- Nested JSON fields that require extraction

## 8. Confidence Rubric

- `High`: business definition confirmed and metrics reconciled
- `Medium`: data pattern is strong but one business mapping is still assumed
- `Low`: key entity, join, or status meaning is still unclear
