-- Intermediate: aggregate event counts per repository.
{{ config(materialized='view') }}

SELECT
    repo_name,
    repo_owner,
    repo_short_name,
    COUNT(*)                            AS total_events,
    COUNT(DISTINCT actor_login)         AS unique_contributors,
    COUNT(DISTINCT event_type)          AS event_type_count,
    MIN(created_at)                     AS first_event_at,
    MAX(created_at)                     AS last_event_at
FROM {{ ref('stg_github_events') }}
WHERE repo_name IS NOT NULL
GROUP BY 1, 2, 3
