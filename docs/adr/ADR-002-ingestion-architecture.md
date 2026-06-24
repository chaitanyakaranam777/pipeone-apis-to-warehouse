# ADR-002: Pull-Based Ingestion with Polling

**Date:** 2024-01-15  **Status:** Accepted

## Context
Need a strategy to ingest from two REST APIs repeatedly.

## Decision
Use **scheduled pull-based polling** via Python + cron/Docker.

## Alternatives
| Option | Pros | Cons |
|---|---|---|
| Webhooks | Real-time | Requires public endpoint |
| Kafka | Scalable | Overkill for scope |
| **Polling (chosen)** | Simple, portable | Minutes of lag |

## Rationale
- No public endpoint needed
- Deduplication handles re-fetches cleanly
- Upgradeable to Airflow/Prefect later

## Consequences
- Data latency up to ~5 minutes (acceptable)
- Must handle rate limits in HTTP client
