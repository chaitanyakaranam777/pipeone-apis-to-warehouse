-- Staging: clean and type-cast raw HN stories
{{ config(materialized='view') }}

SELECT
    hn_id,
    title,
    url,
    CASE
        WHEN url IS NOT NULL THEN SPLIT_PART(REPLACE(url, 'https://', ''), '/', 1)
        ELSE 'self'
    END                           AS domain,
    score,
    author,
    comment_count,
    story_type,
    time_posted::TIMESTAMPTZ      AS time_posted,
    ingested_at
FROM {{ source('raw', 'hn_stories_raw') }}
WHERE hn_id IS NOT NULL
  AND title IS NOT NULL
