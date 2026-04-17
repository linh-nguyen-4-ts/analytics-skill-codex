# Report Template

Use this structure when delivering an insight report.

```markdown
# [Project or Metric Name]
**Period:** [date range]
**Audience:** [audience]
**Confidence:** [High | Medium | Low]

## Key Highlights
- [Most important number] - show absolute and percentage
- [Biggest anomaly or finding]
- [Business implication]

## Metric Definition
- Entity: [application, user, order, account, ...]
- Numerator: [definition]
- Denominator: [definition]
- Counting rule: [COUNT(*) or COUNT(DISTINCT ...)]

## Evidence
- Tables used: [list]
- Query notes: [join path, filters, status mapping]
- Validation checks passed: [list]

## Findings
- [Finding 1]
- [Finding 2]
- [Finding 3]

## Assumptions
- [Assumption 1]
- [Assumption 2]

## Next Checks
- [Action 1]
- [Action 2]
```

## Writing Rules

- Put the decision-relevant summary first.
- Keep the top section scannable.
- Show both count and percentage.
- Name the denominator when presenting a rate.
- Call out unresolved assumptions instead of hiding them.
