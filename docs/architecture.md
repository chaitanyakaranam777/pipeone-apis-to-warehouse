# PipeOne — Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PIPEONE DATA PIPELINE                        │
└─────────────────────────────────────────────────────────────────────┘

  SOURCES               INGESTION              STORAGE
  ─────────             ─────────────          ─────────────────────
  GitHub API    ───►    GitHubClient           PostgreSQL
  (REST v3)     ───►    + Validator    ───►    github_events_raw
                        + Loader               github_repos_raw

  Hacker News   ───►    HNClient               hn_stories_raw
  Firebase API  ───►    + Validator    ───►    ingestion_log
                        + Loader

  TRANSFORM             SERVE
  ─────────────         ──────────────────────────────────────────
  dbt:                  Streamlit Dashboard
    staging/            ├── 🏠 Home (KPIs + pipeline status)
    intermediate/  ►    ├── 🐙 GitHub Analytics
    marts/              ├── 📰 Hacker News Analytics
                        └── 🔗 Combined Dashboard


  INFRASTRUCTURE
  ─────────────────────────────────────────────────────────────────
  Docker Compose:
    ├── postgres    (PostgreSQL 15)
    ├── pipeline    (Python ingestor — runs once then exits)
    └── dashboard   (Streamlit — always running on :8501)

  GitHub Actions CI:
    ├── pytest (tests/ — unit + integration)
    └── docker build (smoke test)
```

## Data Flow

1. `pipeline.py` runs on schedule (or manually)
2. Each client fetches from its API with retry + rate-limit logic
3. Validator cleans and deduplicates records; generates report
4. Loader performs UPSERT into PostgreSQL raw tables
5. Ingestion audit log row written
6. dbt runs: raw → staging views → intermediate views → mart tables
7. Streamlit reads from mart tables (or raw fallback) for dashboard

## Key Design Decisions

See `/docs/adr/` for full Architecture Decision Records:
- ADR-001: PostgreSQL chosen over MongoDB / SQLite
- ADR-002: Pull-based polling chosen over webhooks / streaming
- ADR-003: dbt chosen for transformation layer
