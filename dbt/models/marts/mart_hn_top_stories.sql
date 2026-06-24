-- Mart: top HN stories enriched with domain stats
{{ config(materialized='table') }}

WITH stories AS (
    SELECT * FROM {{ ref('stg_hn_stories') }}
),
domain_stats AS (
    SELECT * FROM {{ ref('int_hn_domain_stats') }}
)

SELECT
    s.hn_id,
    s.title,
    s.url,
    s.domain,
    s.score,
    s.author,
    s.comment_count,
    s.story_type,
    s.time_posted,
    d.story_count        AS domain_story_count,
    d.avg_score          AS domain_avg_score
FROM stories s
LEFT JOIN domain_stats d ON s.domain = d.domain
ORDER BY s.score DESC
LIMIT 200
