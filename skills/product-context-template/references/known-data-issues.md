# Known Data Issues

Log issues that can distort analysis.

## Recommended Format

| Issue | Impact | Detection query or symptom | Workaround | Status |
|------|--------|-----------------------------|------------|--------|
| Example: duplicated service callbacks | inflates raw event counts | `COUNT(*) > COUNT(DISTINCT application_id)` | dedupe by latest callback | open |

## Common Categories

- delayed ingestion
- backfills
- duplicated callbacks or retries
- anonymized keys
- missing partitions
- schema changes over time
- test traffic mixed with production
