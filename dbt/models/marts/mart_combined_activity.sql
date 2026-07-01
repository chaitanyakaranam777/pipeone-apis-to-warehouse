-- Mart: cross-source daily activity for the Combined Dashboard page.
-- Joins GitHub daily counts with HN daily counts on date.
{{ config(materialized='table') }}

WITH gh AS (
    SELECT
        event_date                      AS activity_date,
        SUM(total_events)               AS github_events,
        SUM(unique_actors)              AS github_unique_actors
    FROM {{ ref('mart_github_summary') }}
    GROUP BY 1
),
hn AS (
    SELECT
        DATE_TRUNC('day', time_posted)  AS activity_date,
        COUNT(*)                        AS hn_stories,
        ROUND(AVG(score))               AS hn_avg_score,
        SUM(comment_count)              AS hn_total_comments
    FROM {{ ref('stg_hn_stories') }}
    WHERE time_posted IS NOT NULL
    GROUP BY 1
)

SELECT
    COALESCE(gh.activity_date, hn.activity_date)    AS activity_date,
    COALESCE(gh.github_events, 0)                   AS github_events,
    COALESCE(gh.github_unique_actors, 0)            AS github_unique_actors,
    COALESCE(hn.hn_stories, 0)                      AS hn_stories,
    COALESCE(hn.hn_avg_score, 0)                    AS hn_avg_score,
    COALESCE(hn.hn_total_comments, 0)               AS hn_total_comments
FROM gh
FULL OUTER JOIN hn ON gh.activity_date = hn.activity_date
ORDER BY activity_date DESC
