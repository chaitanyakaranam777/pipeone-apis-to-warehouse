# PipeOne — multi-purpose image
# Used for both the ingestion pipeline and the Streamlit dashboard.

FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Create writable directories
RUN mkdir -p /app/logs /app/dbt/target /app/dbt/dbt_packages

# Make scripts executable
RUN chmod +x /app/scripts/entrypoint.sh \
    && chmod +x /app/scripts/run_pipeline.sh \
    && chmod +x /app/scripts/run_dbt.sh 2>/dev/null || true

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DBT_PROFILES_DIR=/app/dbt

EXPOSE 8501

# Default: launch the dashboard (override with `command:` in docker-compose)
CMD ["streamlit", "run", "dashboard/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
