# Deployment Guide — PipeOne

## Option 1: Render.com (Free, Recommended)

### Step 1: PostgreSQL on Render
1. Go to https://render.com → New → PostgreSQL
2. Name: `pipeone-db`, Region: closest to you, Plan: Free
3. Copy the **Internal Database URL**

### Step 2: Web Service on Render
1. New → Web Service → Connect GitHub repo
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `streamlit run dashboard/app.py --server.port=$PORT --server.address=0.0.0.0`
4. Add environment variables from your `.env`
5. Deploy

---

## Option 2: Railway.app

```bash
npm install -g @railway/cli
railway login
railway init
railway add postgresql
railway up
```

Set env vars in Railway dashboard.

---

## Option 3: Streamlit Community Cloud

1. Push to public GitHub repo
2. Go to https://share.streamlit.io
3. Deploy → select `dashboard/app.py`
4. Add secrets in the Streamlit secrets manager

---

## Option 4: Docker on VPS (DigitalOcean / Hetzner)

```bash
# On your server
git clone https://github.com/YOUR_USERNAME/pipeone.git
cd pipeone
cp .env.example .env && nano .env
docker compose up -d
```

---

## Running the Pipeline on a Schedule

### cron (Linux/Mac)
```cron
# Run pipeline every 30 minutes
*/30 * * * * cd /path/to/pipeone && python ingestion/pipeline.py >> logs/cron.log 2>&1
```

### GitHub Actions (scheduled)
Add to `.github/workflows/ci.yml`:
```yaml
on:
  schedule:
    - cron: '*/30 * * * *'
```
