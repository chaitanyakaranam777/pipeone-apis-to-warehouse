-- Intermediate: count events per actor per day per event type.
-- Used by mart_github_summary for daily analytics.
{{ config(materialized='view') }}

SELECT
    actor_login,
    DATE_TRUNC('day', created_at)   AS event_date,
    event_type,
    repo_owner,
    COUNT(*)                         AS event_count
FROM {{ ref('stg_github_events') }}
WHERE actor_login IS NOT NULL
  AND created_at IS NOT NULL
GROUP BY 1, 2, 3, 4
