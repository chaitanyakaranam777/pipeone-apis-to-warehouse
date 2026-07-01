-- Staging model: clean and normalise raw GitHub events.
-- Extracts owner/repo from the combined repo_name field.
-- Materialized as a view so it always reflects the latest raw data.
{{ config(materialized='view') }}

SELECT
    event_id,
    event_type,
    actor_id,
    actor_login,
    repo_id,
    repo_name,
    SPLIT_PART(repo_name, '/', 1)       AS repo_owner,
    SPLIT_PART(repo_name, '/', 2)       AS repo_short_name,
    public,
    created_at,
    payload_size,
    ingested_at
FROM {{ source('raw', 'github_events_raw') }}
WHERE event_id IS NOT NULL
  AND event_type IS NOT NULL
