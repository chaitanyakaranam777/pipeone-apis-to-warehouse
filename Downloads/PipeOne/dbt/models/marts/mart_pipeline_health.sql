-- Mart: pipeline run history for the Home dashboard page.
-- Shows recent ingestion runs with success/failure status.
{{ config(materialized='table') }}

SELECT
    id,
    pipeline,
    source,
    records_fetched,
    records_inserted,
    records_skipped,
    status,
    error_message,
    started_at,
    finished_at,
    duration_seconds,
    ROUND(
        100.0 * records_inserted / NULLIF(records_fetched, 0), 1
    ) AS insert_rate_pct
FROM {{ ref('stg_ingestion_log') }}
ORDER BY started_at DESC
LIMIT 100
