-- Mart: daily GitHub activity summary by event type.
-- Primary table for the GitHub Analytics dashboard page.
{{ config(materialized='table') }}

SELECT
    event_date,
    event_type,
    SUM(event_count)                AS total_events,
    COUNT(DISTINCT actor_login)     AS unique_actors,
    COUNT(DISTINCT repo_owner)      AS unique_repo_owners
FROM {{ ref('int_github_event_counts') }}
GROUP BY 1, 2
ORDER BY event_date DESC, total_events DESC
