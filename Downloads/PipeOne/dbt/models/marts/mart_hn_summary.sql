{{ config(materialized='table') }}

with stories as (
    select * from {{ ref('stg_hn_stories') }}
)

select
    hn_id,
    title,
    url,
    score,
    author,
    comment_count,
    story_type,
    score_tier,
    time_posted,
    posted_day,
    rank() over (order by score desc)         as score_rank,
    rank() over (order by comment_count desc) as comment_rank
from stories
order by score desc
