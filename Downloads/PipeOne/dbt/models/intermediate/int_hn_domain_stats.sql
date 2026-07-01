-- Intermediate: aggregate story stats by domain.
-- Used by mart_hn_top_stories for domain enrichment.
{{ config(materialized='view') }}

SELECT
    domain,
    COUNT(*)                AS story_count,
    ROUND(AVG(score))       AS avg_score,
    SUM(comment_count)      AS total_comments,
    MAX(score)              AS max_score,
    MIN(score)              AS min_score
FROM {{ ref('stg_hn_stories') }}
GROUP BY 1
