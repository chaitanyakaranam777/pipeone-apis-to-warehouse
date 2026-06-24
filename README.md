# 🚀 PipeOne — APIs to Warehouse

[![CI](https://github.com/YOUR_USERNAME/pipeone/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/pipeone/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)](https://postgresql.org)
[![dbt](https://img.shields.io/badge/dbt-1.7-FF694B.svg)](https://getdbt.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29-FF4B4B.svg)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **H1 Internship Project — Foundations of Data Engineering**  
> End-to-end data pipeline: GitHub + Hacker News APIs → PostgreSQL → dbt → Streamlit Dashboard

---

## 📐 Architecture

```
GitHub API  ──►  Python Ingestor  ──►  PostgreSQL  ──►  dbt  ──►  Streamlit
HN API      ──►  (validate+load)          │                         Dashboard
                                    ingestion_log
```

Full diagram: [`docs/architecture.md`](docs/architecture.md)

---

## ✨ Features

| Feature | Details |
|---|---|
| **API Ingestion** | GitHub Events + Hacker News with pagination, retries, rate-limit handling |
| **Validation** | Field checks, type normalisation, deduplication, validation reports |
| **PostgreSQL** | UPSERT logic, indexes, transactions, audit logging |
| **dbt** | 3-layer model architecture (staging → intermediate → marts) with schema tests |
| **Dashboard** | 4-page Streamlit app: Home, GitHub, HN, Combined — dark mode, charts, search |
| **Docker** | One-command full-stack launch: `docker compose up` |
| **Testing** | pytest suite — unit, integration, DB tests |
| **CI/CD** | GitHub Actions — runs tests + builds Docker image on every push |

---

## 🚀 Quick Start

### Option A — Docker (recommended)

```bash
git clone https://github.com/YOUR_USERNAME/pipeone.git
cd pipeone
cp .env.example .env
# Optional: add your GitHub token to .env for higher rate limits
docker compose up
```

Open **http://localhost:8501** in your browser.

### Option B — Local Python

```bash
# 1. Clone and enter
git clone https://github.com/YOUR_USERNAME/pipeone.git
cd pipeone

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 5. Start PostgreSQL (if not using Docker)
# Make sure PostgreSQL is running and pipeone database exists

# 6. Initialise the database
python scripts/init_db.py

# 7. Run the pipeline
python ingestion/pipeline.py

# 8. (Optional) Run dbt transformations
cd dbt && dbt run && dbt test && cd ..

# 9. Launch the dashboard
streamlit run dashboard/app.py
```

---

## 🧪 Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=term-missing

# Specific test file
pytest tests/test_validator.py -v
```

Tests use SQLite in-memory — **no PostgreSQL required** to run the test suite.

---

## 📁 Project Structure

```
PipeOne/
├── .github/workflows/      # GitHub Actions CI
├── configs/                # Centralised settings (env-driven)
├── database/               # SQLAlchemy models + connection factory
├── dbt/                    # dbt project
│   ├── models/
│   │   ├── staging/        # Type-cast views of raw tables
│   │   ├── intermediate/   # Aggregation + business logic views
│   │   └── marts/          # Final analytics tables
│   ├── macros/             # Reusable SQL macros
│   └── tests/              # dbt schema tests
├── dashboard/              # Streamlit app
│   ├── app.py              # Entry point
│   ├── db_queries.py       # Cached SQL helpers + sample data fallback
│   └── pages/              # Home / GitHub / HN / Combined pages
├── docs/                   # Documentation
│   ├── adr/                # Architecture Decision Records
│   ├── architecture.md
│   ├── reflection.md
│   ├── roadmap.md
│   ├── resume_bullets.md
│   └── mock_interview.md
├── ingestion/              # Pipeline code
│   ├── base_client.py      # HTTP client with retries + rate-limit handling
│   ├── github_client.py    # GitHub API client
│   ├── hn_client.py        # Hacker News API client
│   ├── validator.py        # Data validation + reports
│   ├── loader.py           # PostgreSQL upsert logic
│   └── pipeline.py         # Main orchestrator
├── scripts/                # Utility shell scripts
├── tests/                  # pytest test suite
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and fill in your values:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=pipeone
POSTGRES_USER=pipeone_user
POSTGRES_PASSWORD=pipeone_pass

# Optional but recommended — increases GitHub rate limit from 60 to 5000 req/hr
GITHUB_TOKEN=ghp_your_token_here

LOG_LEVEL=INFO
ENVIRONMENT=development
```

---

## 📊 Dashboard Pages

| Page | Description |
|---|---|
| **🏠 Home** | KPI tiles, pipeline run history, architecture overview |
| **🐙 GitHub Analytics** | Event type breakdown, timeline, top actors, repo search |
| **📰 Hacker News** | Score distribution, top domains, score vs comments scatter |
| **🔗 Combined** | Trending repos, cross-source activity timeline, treemap |

> The dashboard works in **demo mode** with sample data if no database is connected.

---

## ☁️ Deployment (Free Tier)

### Render.com (easiest)
1. Push repo to GitHub
2. Create a new **PostgreSQL** service on Render (free tier)
3. Create a new **Web Service** → connect your repo → set build command: `pip install -r requirements.txt` → start command: `streamlit run dashboard/app.py --server.port=$PORT --server.address=0.0.0.0`
4. Set environment variables from `.env`

### Railway.app
1. Push to GitHub
2. New project → Deploy from GitHub repo
3. Add PostgreSQL plugin
4. Set environment variables
5. Deploy

### Supabase + Streamlit Cloud
1. Create a free PostgreSQL on Supabase
2. Deploy dashboard on [streamlit.io/cloud](https://streamlit.io/cloud)
3. Add Supabase connection string as secret

Full deployment guide: [`docs/deployment.md`](docs/deployment.md)

---

## 📚 Documentation

| Document | Description |
|---|---|
| [Architecture](docs/architecture.md) | System design and data flow |
| [ADR-001](docs/adr/ADR-001-database-choice.md) | Why PostgreSQL |
| [ADR-002](docs/adr/ADR-002-ingestion-architecture.md) | Why polling over streaming |
| [ADR-003](docs/adr/ADR-003-dbt-transformation-layer.md) | Why dbt |
| [Reflection](docs/reflection.md) | Learnings and challenges |
| [Roadmap](docs/roadmap.md) | 3rd year learning roadmap |
| [Resume Bullets](docs/resume_bullets.md) | CV-ready bullet points |
| [Mock Interview](docs/mock_interview.md) | Interview Q&A prep |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| HTTP Client | requests + tenacity |
| Database | PostgreSQL 15 |
| ORM | SQLAlchemy 2.0 |
| Transformation | dbt-postgres 1.7 |
| Dashboard | Streamlit 1.29 + Plotly |
| Containerisation | Docker + Docker Compose |
| Testing | pytest + responses |
| Logging | loguru |
| CI/CD | GitHub Actions |

---

## 🤝 Suggested Commit Messages

```
feat: add GitHub events ingestion with pagination
feat: implement HN top stories pipeline
feat: add data validation with deduplication
feat: create PostgreSQL models with UPSERT logic
feat: add dbt staging and mart models
feat: build Streamlit multi-page dashboard
feat: add Docker Compose full-stack setup
test: add pytest suite for validator and DB models
docs: add ADRs, README, architecture diagram
ci: add GitHub Actions test and build workflow
```

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

*Built as part of the Foundations of Data Engineering internship segment.*
