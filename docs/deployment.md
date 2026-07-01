# PipeOne — Deployment Guide

Three fully-tested free deployment options.

---

## Option 1 — Render.com (Recommended)

### Step 1: PostgreSQL database
1. [render.com](https://render.com) → **New** → **PostgreSQL**
2. Name: `pipeone-db`, Region: nearest, Plan: **Free**
3. After creation, copy the **Internal Database URL** (used internally) and the **External Database URL** (for local testing)

### Step 2: Web Service (Dashboard)
1. **New** → **Web Service** → connect your GitHub repo
2. Settings:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run dashboard/app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
3. **Environment Variables** (add all from `.env`):
   ```
   POSTGRES_HOST     = <from Render PostgreSQL Internal Host>
   POSTGRES_PORT     = 5432
   POSTGRES_DB       = <your db name>
   POSTGRES_USER     = <your db user>
   POSTGRES_PASSWORD = <your db password>
   GITHUB_TOKEN      = <your token>
   PYTHONPATH        = /opt/render/project/src
   ```
4. Click **Deploy**

### Step 3: Cron Job (Pipeline)
1. **New** → **Cron Job** → connect your GitHub repo
2. **Command:** `python ingestion/pipeline.py`
3. **Schedule:** `*/30 * * * *` (every 30 minutes)
4. Add same environment variables as above

---

## Option 2 — Railway.app

```bash
# Install Railway CLI
npm install -g @railway/cli
railway login

# Create project
railway init

# Add PostgreSQL plugin
railway add postgresql

# Deploy
railway up
```

1. In Railway dashboard → **Variables** → add all env vars from `.env`
2. The `Dockerfile` and `docker-compose.yml` are detected automatically
3. Set the start command to: `bash scripts/entrypoint.sh`

---

## Option 3 — Streamlit Community Cloud + Supabase

Best for showcasing the dashboard without running the pipeline continuously.

### Database (Supabase — free)
1. [supabase.com](https://supabase.com) → New Project
2. Copy the **Connection String** (URI format)
3. Run the pipeline locally against Supabase:
   ```bash
   export DATABASE_URL="postgresql://..."
   python ingestion/pipeline.py
   ```

### Dashboard (Streamlit Cloud — free)
1. Push repo to GitHub (must be public for free tier)
2. [share.streamlit.io](https://share.streamlit.io) → **Deploy an app**
3. Select `dashboard/app.py` as the main file
4. **Advanced settings** → **Secrets**:
   ```toml
   POSTGRES_HOST = "db.xxx.supabase.co"
   POSTGRES_PORT = "5432"
   POSTGRES_DB = "postgres"
   POSTGRES_USER = "postgres"
   POSTGRES_PASSWORD = "your-password"
   ```
5. Deploy

---

## Local Docker (Production-like)

```bash
git clone https://github.com/YOUR_USERNAME/pipeone.git
cd pipeone
cp .env.example .env           # fill in GITHUB_TOKEN
docker compose up --build
```

- Dashboard: http://localhost:8501
- PostgreSQL: localhost:5432

---

## Running dbt Manually

```bash
cd dbt/
dbt debug                          # verify connection
dbt run                            # build all models
dbt test                           # run schema tests
dbt docs generate && dbt docs serve  # view lineage in browser
```

---

## Scheduled Pipeline (cron)

```cron
# /etc/crontab — run pipeline every 30 minutes
*/30 * * * * cd /path/to/pipeone && python ingestion/pipeline.py >> logs/cron.log 2>&1
```
