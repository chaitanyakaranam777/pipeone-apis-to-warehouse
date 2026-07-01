-- Intermediate: aggregate event counts per actor.
{{ config(materialized='view') }}

SELECT
    actor_login,
    COUNT(*)                            AS total_events,
    COUNT(DISTINCT repo_name)           AS repos_touched,
    COUNT(DISTINCT event_type)          AS event_types_used,
    MIN(created_at)                     AS first_seen_at,
    MAX(created_at)                     AS last_seen_at
FROM {{ ref('stg_github_events') }}
WHERE actor_login IS NOT NULL
GROUP BY 1
