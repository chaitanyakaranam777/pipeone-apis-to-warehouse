-- Staging model: clean and normalise raw Hacker News stories.
-- Extracts the domain from the URL for later aggregation.
{{ config(materialized='view') }}

SELECT
    hn_id,
    title,
    url,
    CASE
        WHEN url IS NOT NULL AND url != ''
            THEN SPLIT_PART(REPLACE(REPLACE(url, 'https://', ''), 'http://', ''), '/', 1)
        ELSE 'self'
    END                                  AS domain,
    score,
    author,
    comment_count,
    story_type,
    time_posted,
    ingested_at
FROM {{ source('raw', 'hn_stories_raw') }}
WHERE hn_id IS NOT NULL
  AND title IS NOT NULL
  AND TRIM(title) != ''
