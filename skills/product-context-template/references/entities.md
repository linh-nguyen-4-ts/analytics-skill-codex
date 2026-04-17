# Entities

Document the business entities that matter for analysis.

## Recommended Format

| Entity | Business meaning | Table or view | Grain | Stable key | Common joins |
|--------|------------------|---------------|-------|------------|--------------|
| Example: application | One submitted onboarding application | `dop.applications` | 1 row per application | `id` | `application_services.application_id` |

## Questions to Answer

- What is the entity that business cares about?
- Which ID is stable across retries and state changes?
- Which tables store snapshots versus events?
- Which joins are known-safe?
