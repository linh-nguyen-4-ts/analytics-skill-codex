# Metrics

Define KPIs in a way that can be translated into SQL without guesswork.

## Recommended Format

| Metric | Business question | Numerator | Denominator | Counting rule | Filters | Notes |
|--------|-------------------|-----------|-------------|---------------|---------|-------|
| Example: approval_rate | How many applications were approved? | distinct approved applications | distinct submitted applications | `COUNT(DISTINCT application_id)` | lender_id = 9 | exclude test traffic |

## Questions to Answer

- Which entity should be counted?
- Is the metric event-based or entity-based?
- Which filters are mandatory?
- Which breakdowns matter most?
- What official number should this metric reconcile against?
