# Intake Checklist

Use this file when a user asks for data insight on a new database, table group, or product flow.

## Minimum Questions

Ask only what the database cannot confirm by itself:

1. What business question or decision should this analysis support?
2. What time range matters?
3. What is the entity of record for counting?
4. Should the numerator and denominator use raw rows or distinct entities?
5. What does success, failure, and in-progress mean in business terms?
6. Is there an existing dashboard, report, or stakeholder number to reconcile against?
7. Who is the audience?

## Nice-to-Have Questions

- Is there a Jira, PRD, Confluence page, or data dictionary?
- Are there known bugs, backfills, or data quality issues?
- Are there tables people trust more than others?
- Which drill-downs matter most: date, batch, product, partner, channel, status, reason code?

## Good Default Behavior

- Proceed after the minimum questions if the user is busy.
- Keep assumptions explicit and revisitable.
- Use the first schema discovery pass to reduce follow-up questions.

## Red Flags

Pause and ask a direct clarification when any of these appear:

- more than one plausible entity key
- more than one plausible source-of-truth table
- status values that need business mapping
- count discrepancies against an official number
- lifecycle steps that happen out of order
