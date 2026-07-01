{{ config(materialized='table') }}

with stories as (

    select *
    from {{ ref('stg_hn_stories') }}

)

select
    hn_id,
    title,
    url,
    score,
    author,
    comment_count,
    story_type,
    case
        when score >= 500 then 'Viral'
        when score >= 200 then 'Trending'
        when score >= 100 then 'Popular'
        when score >= 50 then 'Good'
        else 'Normal'
    end as score_tier,
    time_posted,
    posted_day,
    rank() over (order by score desc) as score_rank,
    rank() over (order by comment_count desc) as comment_rank
from stories
order by score desc