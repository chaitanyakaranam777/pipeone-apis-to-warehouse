# 3rd Year Learning Roadmap — Data Engineering

Building on the PipeOne foundation, here is a structured 12-month roadmap for Year 3.

## Q1 — Advanced Pipeline Engineering (Months 1-3)

### Orchestration
- [ ] Apache Airflow: DAGs, operators, XComs, connections
- [ ] Prefect (modern alternative): flows, tasks, deployments

### Streaming
- [ ] Apache Kafka: producers, consumers, topics, partitions
- [ ] Spark Structured Streaming basics

### Cloud
- [ ] AWS: S3, RDS, Lambda, Glue (or GCP: BigQuery, Cloud Functions, Dataflow)
- [ ] Terraform for infrastructure-as-code

**Project:** Rebuild PipeOne with Airflow + S3 + Redshift

---

## Q2 — Data Warehousing & Analytics Engineering (Months 4-6)

### Warehouses
- [ ] Snowflake: architecture, virtual warehouses, Time Travel
- [ ] BigQuery: partitioning, clustering, nested schemas
- [ ] dbt Advanced: incremental models, snapshots, macros, packages

### Data Modelling
- [ ] Kimball dimensional modelling (star schema)
- [ ] Data Vault 2.0 basics
- [ ] Slowly Changing Dimensions (SCD Types 1/2)

**Project:** Build a Snowflake-backed analytics warehouse with dbt Cloud

---

## Q3 — Data Quality & Observability (Months 7-9)

- [ ] Great Expectations: expectations, data docs, checkpoints
- [ ] Monte Carlo / re_data: anomaly detection
- [ ] OpenLineage & Marquez for data lineage
- [ ] Prometheus + Grafana for pipeline metrics

**Project:** Add full observability layer to PipeOne

---

## Q4 — Internship Prep & Portfolio (Months 10-12)

- [ ] Contribute to open-source dbt packages
- [ ] Build a capstone project end-to-end (streaming + warehouse + dashboard)
- [ ] LeetCode SQL (top 50 analytics questions)
- [ ] System design practice: design a data lake, design a real-time dashboard
- [ ] Mock interviews with peers

**Target Companies:** Databricks, Snowflake, dbt Labs, Stripe, Airbnb, Amazon

---

## Resources

| Topic | Resource |
|---|---|
| dbt | dbt Learn (free), Fundamentals course |
| Airflow | Astronomer Academy |
| Kafka | Confluent Developer training |
| Spark | Databricks Academy |
| SQL | Mode Analytics SQL Tutorial, pgexercises.com |
| System Design | "Designing Data-Intensive Applications" (Kleppmann) |
