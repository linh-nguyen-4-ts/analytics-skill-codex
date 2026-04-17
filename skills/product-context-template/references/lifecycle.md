# Lifecycle

Document the state machine or process flow for the product.

## Recommended Format

| Stage | Business meaning | Technical status or state | Entry condition | Exit condition | Repeats |
|-------|------------------|---------------------------|-----------------|----------------|---------|
| Example: submitted | User created an application | `submitted` | row created | moved to review | no |

## Questions to Answer

- Which statuses count as success, failure, cancel, pending, or retry?
- Can the same stage happen more than once?
- Which timestamp represents entry into the stage?
- Which technical statuses should not be shown as business stages?
