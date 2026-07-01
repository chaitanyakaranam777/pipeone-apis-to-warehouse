-- Mart: top repositories ranked by total event volume.
-- Used by the Combined Dashboard trending repos section.
{{ config(materialized='table') }}

SELECT
    repo_name,
    repo_owner,
    repo_short_name,
    total_events,
    unique_contributors,
    event_type_count,
    first_event_at,
    last_event_at
FROM {{ ref('int_repo_activity') }}
ORDER BY total_events DESC
LIMIT 50
