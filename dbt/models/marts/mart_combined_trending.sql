{{ config(materialized='table') }}

-- Combined view: most-active GitHub repos alongside top HN stories
-- Useful for correlation analysis in the Mini Extension dashboard

with github as (
    select
        'github'        as source,
        repo_name       as name,
        null            as url,
        total_events    as score_or_activity,
        unique_contributors as engagement,
        last_event_at       as published_at
    from {{ ref('mart_repo_leaderboard') }}
    limit 20
),

hn as (
    select
        'hacker_news'   as source,
        title           as name,
        url,
        score           as score_or_activity,
        comment_count   as engagement,
        time_posted     as published_at
    from {{ ref('mart_hn_summary') }}
    where score_rank <= 20
),

combined as (
    select * from github
    union all
    select * from hn
)

select
    source,
    name,
    url,
    score_or_activity,
    engagement,
    published_at,
    rank() over (partition by source order by score_or_activity desc) as source_rank
from combined
order by source, source_rank
