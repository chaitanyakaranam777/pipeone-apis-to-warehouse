# ADR-001: Choose PostgreSQL as the Primary Data Store

**Date:** 2024-01-15  **Status:** Accepted

## Context
PipeOne needs a persistent store for structured API data with upsert support and dbt compatibility.

## Decision
Use **PostgreSQL 15** as the primary data store.

## Alternatives
| Option | Pros | Cons |
|---|---|---|
| PostgreSQL | SQL-standard, dbt-native, free | Requires hosting |
| SQLite | Zero-config | No concurrent writes |
| MongoDB | Schemaless | Weak dbt support |

## Rationale
- dbt has first-class PostgreSQL support
- Native UPSERT via `ON CONFLICT`
- Runs in Docker locally; free hosting on Supabase/Railway/Render

## Consequences
- Needs Docker for local dev
- Production requires hosted PostgreSQL
