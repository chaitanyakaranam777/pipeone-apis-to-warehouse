# Resume Bullets — PipeOne Internship Project

Use these bullets for your CV/resume under a "Projects" or "Experience" section.

---

## Strong Bullets (Action → Tech → Impact)

- Built an end-to-end Python data pipeline ingesting 300+ events/run from GitHub and Hacker News APIs, implementing pagination, exponential back-off retry logic, and rate-limit handling

- Designed a PostgreSQL schema with UPSERT logic (`ON CONFLICT`) to achieve idempotent loads, eliminating duplicate records across pipeline re-runs

- Engineered a three-layer dbt transformation architecture (staging → intermediate → marts) with automated schema tests, reducing analytics query complexity by abstracting raw API payloads

- Developed a multi-page Streamlit analytics dashboard featuring event-type breakdowns, trending repositories, cross-source timelines, and interactive filters with Plotly charts

- Containerised the full stack (PostgreSQL, Python pipeline, Streamlit) with Docker Compose, enabling single-command deployment (`docker compose up`) for reproducible environments

- Implemented structured logging with `loguru`, validation reports, and an ingestion audit table, providing end-to-end observability across all pipeline stages

- Achieved 95%+ test coverage for validation and database modules using pytest with SQLite in-memory fixtures; integrated automated testing in GitHub Actions CI/CD

---

## One-Liner Summaries (for LinkedIn / intro sentences)

- "Designed and deployed a production-grade ETL pipeline from REST APIs to PostgreSQL with dbt transformations and Streamlit dashboards, containerised with Docker."

- "Built PipeOne: an end-to-end data engineering project (API → validation → PostgreSQL → dbt → dashboard) demonstrating the full analytics stack used at companies like dbt Labs, Snowflake, and Databricks."
