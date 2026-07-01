# ADR-003: Use dbt for SQL Transformations

**Date:** 2024-01-15  **Status:** Accepted

## Context
Raw tables need cleaning and aggregation before dashboard use.

## Decision
Use **dbt** with a three-layer model architecture.

## Model Layers
```
staging/      — type casting, renaming, light cleaning
intermediate/ — joins, business-logic aggregations
marts/        — final analytics-ready tables
```

## Rationale
- Industry-standard analytics engineering tool
- Built-in testing (`not_null`, `unique`)
- Auto-generates docs and lineage graphs
- Directly applicable in internship/job roles

## Consequences
- dbt must run after each ingestion cycle
- `profiles.yml` must stay in sync with env vars
