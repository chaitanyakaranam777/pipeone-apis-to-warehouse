# 🚀 PipeOne — APIs to Warehouse

[![CI](https://github.com/YOUR_USERNAME/pipeone/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/pipeone/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)](https://postgresql.org)
[![dbt](https://img.shields.io/badge/dbt-1.7-FF694B.svg)](https://getdbt.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29-FF4B4B.svg)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docker.com)
[![Tests](https://img.shields.io/badge/tests-36%20passing-brightgreen.svg)](#testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **H1 Internship Project — Foundations of Data Engineering (5 Weeks)**
> Complete end-to-end data pipeline: GitHub Events + Hacker News APIs → PostgreSQL → dbt → Streamlit

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PIPEONE PIPELINE                            │
├───────────┬─────────────────┬──────────────┬──────────┬────────────┤
│  SOURCES  │   INGESTION     │   STORAGE    │TRANSFORM │   SERVE    │
├───────────┼─────────────────┼──────────────┼──────────┼────────────┤
│ GitHub    │ base_client.py  │              │ staging/ │            │
│ Events    │ (retries +      │ PostgreSQL   │          │ Streamlit  │
│ API   ───►│ rate limits)    │ ──────────── │ interme- │ Dashboard  │
│           │ github_client   │ events_raw   │ diate/   │ (4 pages)  │
│ Hacker    │ validator.py    │ stories_raw  │          │            │
│ News  ───►│ (dedup +        │ ingestion_   │ marts/   │            │
│ API       │ validation)     │ log          │          │            │
│           │ loader.py       │              │ dbt run  │            │
│           │ (UPSERT)        │              │ dbt test │            │
└───────────┴─────────────────┴──────────────┴──────────┴────────────┘
                                                   Docker Compose
```

---

## Features

| Layer | Technology | What it does |
|---|---|---|
| **Ingestion** | Python + requests + tenacity | Fetches GitHub Events + HN stories; handles pagination, retries, rate limits |
| **Validation** | pandas | Deduplication, type normalisation, field checks, validation reports |
| **Storage** | PostgreSQL 15 + SQLAlchemy | UPSERT with `ON CONFLICT`, indexes, transactions, ingestion audit log |
| **Transform** | dbt 1.7 | 3-layer architecture: staging → intermediate → marts; schema tests |
| **Dashboard** | Streamlit + Plotly | 4 pages; queries dbt marts, falls back to raw tables, then demo data |
| **Docker** | Docker Compose | One command: `docker compose up` starts everything |
| **Testing** | pytest | 36 tests: clients (mocked), validator, loader (SQLite), database (SQLite) |
| **CI/CD** | GitHub Actions | Tests + Docker build on every push |

---

## Quick Start

### Option A — Docker (one command)

```bash
git clone https://github.com/YOUR_USERNAME/pipeone.git
cd pipeone
cp .env.example .env
# Optional: add GITHUB_TOKEN to .env for 5,000 req/hr (default: 60)
docker compose up --build
```

Open **http://localhost:8501** — the dashboard is live.

The startup sequence inside Docker:
1. PostgreSQL starts and becomes healthy
2. Python pipeline runs (fetches GitHub + HN data)
3. dbt transformations run (staging → marts)
4. Streamlit starts on port 8501

### Option B — Local Python

```bash
git clone https://github.com/YOUR_USERNAME/pipeone.git
cd pipeone

# Virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# Initialise database tables
python scripts/init_db.py

# Run the ingestion pipeline
python ingestion/pipeline.py

# (Optional) Run dbt transformations
cd dbt && dbt run && dbt test && cd ..

# Launch dashboard
streamlit run dashboard/app.py
```

> **Demo mode**: The dashboard works without any database — it displays sample data automatically so you can explore all pages before running the pipeline.

---

## Testing

```bash
# Run all 36 tests (no PostgreSQL needed)
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=term-missing

# Single module
pytest tests/test_loader.py -v
```

**Expected:** `36 passed`

Test coverage:
| File | Tests | What's covered |
|---|---|---|
| `test_clients.py` | 6 | GitHub + HN HTTP clients with mocked responses |
| `test_validator.py` | 12 | Validation, deduplication, field normalisation |
| `test_loader.py` | 10 | UPSERT logic, conflict handling, audit logging |
| `test_database.py` | 8 | ORM models, constraints, connection |

---

## Project Structure

```
PipeOne/
├── .github/workflows/ci.yml         # GitHub Actions: test + docker build
├── configs/settings.py              # Central config — all values from .env
├── database/
│   ├── models.py                    # SQLAlchemy ORM: 4 tables
│   └── connection.py                # Engine, sessions, health check
├── ingestion/
│   ├── base_client.py               # HTTP client: retries + rate-limit handling
│   ├── github_client.py             # GitHub Events API + trending repos
│   ├── hn_client.py                 # Hacker News Firebase API
│   ├── validator.py                 # Validation, dedup, ValidationReport
│   ├── loader.py                    # PostgreSQL UPSERT + audit log (SQLite fallback)
│   └── pipeline.py                  # Orchestrator: DB wait → GitHub → HN → log
├── dbt/
│   ├── dbt_project.yml              # dbt project config
│   ├── profiles.yml                 # DB connection (reads from env vars)
│   └── models/
│       ├── staging/                 # stg_github_events, stg_hn_stories, stg_ingestion_log
│       ├── intermediate/            # int_github_event_counts, int_hn_domain_stats,
│       │                            # int_repo_activity, int_actor_activity
│       └── marts/                   # mart_github_summary, mart_hn_top_stories,
│                                    # mart_combined_activity, mart_repo_leaderboard,
│                                    # mart_pipeline_health
├── dashboard/
│   ├── app.py                       # Streamlit entry point + routing
│   ├── db_queries.py                # Mart-first queries with raw + demo fallback
│   └── pages/
│       ├── home.py                  # KPIs, pipeline health chart, architecture
│       ├── github.py                # Event analytics, top actors, timeline
│       ├── hackernews.py            # Score histogram, domains, scatter, search
│       └── combined.py             # Dual-axis timeline, treemap, side-by-side
├── docs/
│   ├── adr/ADR-001-*.md             # Why PostgreSQL
│   ├── adr/ADR-002-*.md             # Why pull-based polling
│   ├── adr/ADR-003-*.md             # Why dbt
│   ├── architecture.md
│   ├── deployment.md                # Render / Railway / Streamlit Cloud
│   ├── reflection.md
│   ├── roadmap.md
│   ├── resume_bullets.md
│   └── mock_interview.md
├── scripts/
│   ├── entrypoint.sh                # Docker startup: DB wait → pipeline → dbt → streamlit
│   ├── init_db.py                   # Create all tables
│   ├── run_pipeline.sh
│   └── run_dbt.sh
├── tests/
│   ├── conftest.py
│   ├── test_clients.py
│   ├── test_validator.py
│   ├── test_loader.py               # NEW: loader UPSERT + audit log tests
│   └── test_database.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Environment Variables

```env
# Database (required)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=pipeone
POSTGRES_USER=pipeone_user
POSTGRES_PASSWORD=pipeone_pass

# GitHub token (optional — raises API limit from 60 to 5,000 req/hr)
# Get one at: https://github.com/settings/tokens
GITHUB_TOKEN=ghp_your_token_here

# Application
LOG_LEVEL=INFO
ENVIRONMENT=development
```

---

## Dashboard Pages

| Page | Data Source | Key Visualisations |
|---|---|---|
| **🏠 Home** | `mart_pipeline_health` | KPI tiles, run history bar chart, architecture diagram |
| **🐙 GitHub Analytics** | `mart_github_summary` + raw | Event type bar/pie, activity timeline, top actors, hourly heatmap, stacked bar |
| **📰 Hacker News** | `mart_hn_top_stories` | Score histogram, top domains, score vs comments scatter, domain enrichment |
| **🔗 Combined** | `mart_combined_activity` + `mart_repo_leaderboard` | Dual-axis timeline, trending repos, treemap, pipeline health chart |

All pages gracefully degrade: **dbt mart → raw PostgreSQL → sample data**.

---

## dbt Model Layers

```
staging/                    ← Views over raw tables (type-cast, renamed)
  stg_github_events
  stg_hn_stories
  stg_ingestion_log

intermediate/               ← Business logic aggregations (views)
  int_github_event_counts   — events per actor per day
  int_hn_domain_stats       — story counts and avg score by domain
  int_repo_activity         — event counts per repository
  int_actor_activity        — event counts per actor

marts/                      ← Analytics-ready tables (materialised)
  mart_github_summary       — daily event counts by type
  mart_hn_top_stories       — top stories enriched with domain stats
  mart_combined_activity    — cross-source daily activity
  mart_repo_leaderboard     — top 50 repos by event volume
  mart_pipeline_health      — ingestion run history with success rates
```

---

## Suggested Commit Timeline

```
git commit -m "Week 1: Initial PipeOne data engineering project"
git commit -m "Week 2: Completed GitHub and Hacker News API ingestion pipeline"
git commit -m "Week 3: Added dbt warehouse transformations and analytics dashboard"
git commit -m "Week 4: Added testing, Docker deployment and documentation"
git commit -m "Week 5: Final polish, deployment and presentation ready"
```

---

## Deployment

See [`docs/deployment.md`](docs/deployment.md) for full instructions.

**Free options:**
- **Render.com** — PostgreSQL + Web Service + Cron Job (all free tier)
- **Railway.app** — PostgreSQL + Deployment (Docker Compose detected)
- **Streamlit Community Cloud** + **Supabase** — dashboard + managed DB

---

## Documentation

| File | Description |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | Full system design and data flow |
| [`docs/adr/ADR-001`](docs/adr/ADR-001-database-choice.md) | Why PostgreSQL |
| [`docs/adr/ADR-002`](docs/adr/ADR-002-ingestion-architecture.md) | Why polling over streaming |
| [`docs/adr/ADR-003`](docs/adr/ADR-003-dbt-transformation-layer.md) | Why dbt |
| [`docs/reflection.md`](docs/reflection.md) | Learnings and challenges |
| [`docs/roadmap.md`](docs/roadmap.md) | 12-month Year 3 roadmap |
| [`docs/resume_bullets.md`](docs/resume_bullets.md) | CV-ready bullet points |
| [`docs/mock_interview.md`](docs/mock_interview.md) | Interview Q&A prep |

---

## License

MIT — see [LICENSE](LICENSE)

---
*Built as part of the H1 Foundations of Data Engineering internship segment.*
