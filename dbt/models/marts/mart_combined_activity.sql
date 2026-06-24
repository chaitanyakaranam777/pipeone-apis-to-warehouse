-- Mart: combined GitHub + HN daily activity for cross-source analysis
{{ config(materialized='table') }}

WITH gh AS (
    SELECT
        event_date       AS activity_date,
        SUM(total_events) AS github_events,
        SUM(unique_actors) AS github_actors
    FROM {{ ref('mart_github_summary') }}
    GROUP BY 1
),
hn AS (
    SELECT
        DATE_TRUNC('day', time_posted) AS activity_date,
        COUNT(*)                        AS hn_stories,
        AVG(score)::INT                 AS hn_avg_score
    FROM {{ ref('stg_hn_stories') }}
    GROUP BY 1
)

SELECT
    COALESCE(gh.activity_date, hn.activity_date) AS activity_date,
    COALESCE(gh.github_events, 0)                AS github_events,
    COALESCE(gh.github_actors, 0)                AS github_actors,
    COALESCE(hn.hn_stories, 0)                   AS hn_stories,
    COALESCE(hn.hn_avg_score, 0)                 AS hn_avg_score
FROM gh
FULL OUTER JOIN hn ON gh.activity_date = hn.activity_date
ORDER BY activity_date DESC
