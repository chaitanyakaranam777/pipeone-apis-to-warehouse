{{ config(materialized='view') }}

with events as (
    select * from {{ ref('stg_github_events') }}
),

repo_stats as (
    select
        repo_name,
        repo_owner,
        repo_short_name,
        repo_id,
        count(*)                                    as total_events,
        count(distinct actor_login)                 as unique_actors,
        min(created_at)                             as first_event,
        max(created_at)                             as last_event,
        count(*) filter (where event_type = 'PushEvent')        as pushes,
        count(*) filter (where event_type = 'PullRequestEvent') as pull_requests,
        count(*) filter (where event_type = 'IssuesEvent')      as issues,
        count(*) filter (where event_type = 'WatchEvent')       as watches,
        count(*) filter (where event_type = 'ForkEvent')        as forks
    from events
    where repo_name is not null
    group by repo_name, repo_owner, repo_short_name, repo_id
)

select * from repo_stats
