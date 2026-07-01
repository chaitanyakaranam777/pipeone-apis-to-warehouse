# Mock Interview Questions — PipeOne Project

Practise answering these in the STAR format (Situation, Task, Action, Result).

---

## Technical Deep-Dives

**Q1. Walk me through the architecture of PipeOne.**
> Tip: Ingestion → Validation → PostgreSQL → dbt → Streamlit. Mention Docker and CI.

**Q2. How did you handle API rate limits?**
> Tip: Explain `X-RateLimit-Remaining` header checks and `Retry-After` sleep logic in `BaseAPIClient`.

**Q3. Why did you choose PostgreSQL over other databases like MongoDB or DuckDB?**
> Tip: Reference ADR-001. Key reasons: dbt-native, SQL standard, UPSERT support, free hosting options.

**Q4. What does `ON CONFLICT DO NOTHING` do? When would you use `DO UPDATE` instead?**
> Tip: DO NOTHING skips duplicates silently. DO UPDATE (upsert) is used for mutable fields like score, comment_count.

**Q5. Explain the three-layer dbt model architecture.**
> Tip: Staging = clean + type-cast. Intermediate = business logic. Marts = final analytics tables.

**Q6. What are dbt tests? Name two you used.**
> Tip: Schema tests check data quality. Used `not_null` and `unique` on primary keys.

**Q7. How does your pipeline handle failures gracefully?**
> Tip: Try/except in each client, logging errors without crashing, ingestion log with status field.

**Q8. How would you scale this pipeline to handle 10x the data volume?**
> Tip: Add Kafka for streaming, partition PostgreSQL tables by date, use incremental dbt models, switch to Spark for transformation.

---

## Behavioural Questions

**Q9. Tell me about a technical challenge you faced and how you solved it.**
> Tip: Example — GitHub pagination returning duplicates → added `seen_ids` set in client.

**Q10. How did you ensure code quality in this project?**
> Tip: PEP8, type hints, docstrings, pytest coverage, GitHub Actions CI.

**Q11. What would you do differently if you had another week?**
> Tip: Add Airflow for scheduling, add Great Expectations for data quality, deploy to Railway/Render.

**Q12. How does this project demonstrate production-readiness?**
> Tip: Environment variables, no hardcoded secrets, Docker, logging, error handling, CI/CD, README.
