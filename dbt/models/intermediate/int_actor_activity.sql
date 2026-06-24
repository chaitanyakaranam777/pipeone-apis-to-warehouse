{{ config(materialized='view') }}

with events as (
    select * from {{ ref('stg_github_events') }}
),

actor_stats as (
    select
        actor_login,
        actor_id,
        count(*)                                    as total_events,
        count(distinct event_type)                  as distinct_event_types,
        count(distinct repo_name)                   as distinct_repos,
        min(created_at)                             as first_seen,
        max(created_at)                             as last_seen,
        count(*) filter (where event_type = 'PushEvent')        as push_count,
        count(*) filter (where event_type = 'PullRequestEvent') as pr_count,
        count(*) filter (where event_type = 'IssuesEvent')      as issue_count,
        count(*) filter (where event_type = 'WatchEvent')       as watch_count
    from events
    where actor_login is not null
    group by actor_login, actor_id
)

select * from actor_stats
