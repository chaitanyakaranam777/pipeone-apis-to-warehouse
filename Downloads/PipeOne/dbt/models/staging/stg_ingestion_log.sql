-- Staging model: ingestion audit log.
{{ config(materialized='view') }}

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
    EXTRACT(EPOCH FROM (finished_at - started_at)) AS duration_seconds
FROM {{ source('raw', 'ingestion_log') }}
WHERE pipeline IS NOT NULL
