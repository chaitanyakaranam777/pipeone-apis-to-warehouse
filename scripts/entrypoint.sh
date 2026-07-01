#!/usr/bin/env bash
# Docker entrypoint for the dashboard service.
# Sequence:
#   1. Wait for PostgreSQL to be reachable
#   2. Run the Python ingestion pipeline (init DB + fetch data)
#   3. Run dbt transformations (optional — skipped gracefully if dbt not ready)
#   4. Launch the Streamlit dashboard

set -euo pipefail

log() { echo "[entrypoint] $(date '+%H:%M:%S') — $*"; }

# ── 1. Wait for PostgreSQL ────────────────────────────────────────────────────
log "Waiting for PostgreSQL at ${POSTGRES_HOST:-localhost}:${POSTGRES_PORT:-5432}..."
MAX_WAIT=60
WAITED=0
until python -c "
import sys, os
sys.path.insert(0, '/app')
from database.connection import health_check
sys.exit(0 if health_check() else 1)
" 2>/dev/null; do
    if [ "$WAITED" -ge "$MAX_WAIT" ]; then
        log "ERROR: PostgreSQL not ready after ${MAX_WAIT}s. Starting dashboard in demo mode."
        break
    fi
    log "  PostgreSQL not ready, retrying in 3s..."
    sleep 3
    WAITED=$((WAITED + 3))
done
log "PostgreSQL check complete."

# ── 2. Run ingestion pipeline ─────────────────────────────────────────────────
log "Running ingestion pipeline..."
python /app/ingestion/pipeline.py && log "Pipeline completed successfully." \
    || log "WARNING: Pipeline finished with errors — dashboard will show partial data."

# ── 3. Run dbt transformations ────────────────────────────────────────────────
if command -v dbt &>/dev/null; then
    log "Running dbt transformations..."
    cd /app/dbt
    dbt run --profiles-dir /app/dbt --project-dir /app/dbt 2>&1 \
        && log "dbt run completed." \
        || log "WARNING: dbt run failed — dashboard will query raw tables."
    dbt test --profiles-dir /app/dbt --project-dir /app/dbt 2>&1 \
        && log "dbt test passed." \
        || log "WARNING: dbt tests failed."
    cd /app
else
    log "dbt not found — skipping transformations."
fi

# ── 4. Launch Streamlit ───────────────────────────────────────────────────────
log "Starting Streamlit dashboard on port 8501..."
exec streamlit run /app/dashboard/app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
