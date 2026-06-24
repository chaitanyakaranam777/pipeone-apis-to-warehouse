-- Intermediate: aggregate HN stories by domain
{{ config(materialized='view') }}

SELECT
    domain,
    COUNT(*)            AS story_count,
    AVG(score)::INT     AS avg_score,
    SUM(comment_count)  AS total_comments,
    MAX(score)          AS max_score
FROM {{ ref('stg_hn_stories') }}
GROUP BY 1
HAVING COUNT(*) >= 1
ORDER BY story_count DESC
