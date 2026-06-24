-- Staging: clean and type-cast raw GitHub events
{{ config(materialized='view') }}

SELECT
    event_id,
    event_type,
    actor_id,
    actor_login,
    repo_id,
    repo_name,
    SPLIT_PART(repo_name, '/', 1)  AS repo_owner,
    SPLIT_PART(repo_name, '/', 2)  AS repo_short_name,
    public,
    created_at::TIMESTAMPTZ        AS created_at,
    payload_size,
    ingested_at
FROM {{ source('raw', 'github_events_raw') }}
WHERE event_id IS NOT NULL
  AND event_type IS NOT NULL
