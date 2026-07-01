# Internship Reflection — H1 PipeOne

**Segment:** Foundations of Data Engineering  
**Duration:** 5 Weeks  
**Project:** H1 — APIs to Warehouse (PipeOne)

## What I Built

PipeOne is a production-inspired end-to-end data pipeline that:
1. Ingests data from two public APIs (GitHub Events, Hacker News)
2. Validates and cleans the data in Python
3. Stores it in PostgreSQL with UPSERT logic
4. Transforms it via dbt (staging → intermediate → marts)
5. Visualises it in a multi-page Streamlit dashboard
6. Packages everything in Docker for reproducible deployment

## Key Technical Learnings

### Data Ingestion Patterns
- Implemented retry logic with exponential back-off using `tenacity`
- Learned to handle API rate limits via `X-RateLimit-*` headers
- Built a base HTTP client that all API clients inherit from (DRY principle)

### Data Validation
- Understood why validation before loading is critical — bad data compounds downstream
- Implemented field-level checks, type normalisation, and deduplication
- Generated structured validation reports for observability

### PostgreSQL & SQLAlchemy
- Used `ON CONFLICT DO NOTHING / DO UPDATE` for idempotent loads
- Implemented connection pooling and transactional sessions via context managers
- Designed indexes strategically (on `created_at`, `actor_login`, `event_type`)

### dbt
- Understood the layered transformation philosophy (raw → staging → marts)
- Wrote Jinja-templated SQL models with `{{ ref() }}` and `{{ source() }}`
- Added schema tests to catch data quality issues automatically

### Streamlit
- Built multi-page dashboards with sidebar navigation
- Used `@st.cache_data` for performance
- Added graceful fallback to sample data when DB is unavailable

### Docker & DevOps
- Containerised the full stack (Postgres + pipeline + dashboard)
- Wrote a `docker-compose.yml` with health checks and service dependencies
- Set up GitHub Actions CI for automated testing

## Challenges & How I Solved Them

| Challenge | Solution |
|---|---|
| API rate limits on GitHub | Checked `X-RateLimit-Remaining`, slept until reset |
| Duplicate events on re-runs | `ON CONFLICT DO NOTHING` in PostgreSQL |
| Streamlit crashes without DB | Graceful fallback to sample DataFrames |
| dbt can't run without live DB | Made dbt optional in Docker Compose |

## What I Would Do Differently

- Add an orchestration layer (Airflow or Prefect) for scheduling
- Implement incremental dbt models for efficiency at scale
- Add Great Expectations for more rigorous data quality checks
- Set up Grafana + Prometheus for pipeline observability

## Impact & Transferable Skills

- **System design thinking**: breaking a problem into ingestion → storage → transform → serve layers
- **Production habits**: logging, error handling, environment variables, no hardcoded secrets
- **Collaboration readiness**: README, ADRs, commit conventions, CI/CD
