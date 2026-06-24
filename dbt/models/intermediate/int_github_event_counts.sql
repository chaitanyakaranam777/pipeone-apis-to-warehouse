-- Intermediate: count events per actor per day
{{ config(materialized='view') }}

SELECT
    actor_login,
    DATE_TRUNC('day', created_at)  AS event_date,
    event_type,
    COUNT(*)                        AS event_count
FROM {{ ref('stg_github_events') }}
WHERE actor_login IS NOT NULL
GROUP BY 1, 2, 3
