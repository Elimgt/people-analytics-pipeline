# People Analytics Pipeline

A data pipeline that simulates an ATS/HRIS export (job requisitions, candidates, recruiting funnel stages, offers), transforms it with dbt into recruiting metrics, and orchestrates it daily with Airflow.

Designed around real recruiting processes (funnel stages, sourcing channels, time-to-hire and offer-acceptance metrics) — the goal is to show what a Data Engineering pipeline looks like when applied to People Analytics.

## Architecture

```
generate_data.py → raw CSVs (simulate an ATS/HRIS export)
        │  load_data.py
        ▼
  Postgres (raw schema)
        │  dbt run
        ▼
  Postgres (analytics schema: staging → marts)
        │
        ▼
  metrics: time-to-hire, offer acceptance rate,
  funnel conversion by stage, source effectiveness

Orchestrated by Airflow (Docker) · Tested with dbt tests · CI on GitHub Actions
```

## Data model

- `job_requisitions`: open/closed roles by department
- `candidates`: candidates, recruiting source, and which role they applied to
- `pipeline_stages`: funnel stage history per candidate (Applied → Screening → Interview → Offer → Hired/Rejected)
- `offers`: offers made, whether accepted, and when

## Metrics (`dbt_project/models/marts`)

- `fct_hiring_funnel`: candidates by stage and requisition
- `fct_time_to_hire`: days from application to hire
- `fct_offer_acceptance`: offer acceptance rate
- `fct_source_effectiveness`: hire rate by recruiting source

## How to run it locally

1. Prerequisites: Docker Desktop, Python 3.11, dbt (`pip install -r requirements.txt`).
2. Start the database and Airflow: `docker compose up -d --build`
3. Generate sample data: `python src/generate_data.py`
4. Load it into Postgres: `python src/load_data.py`
5. Transform with dbt: `cd dbt_project && dbt run --profiles-dir . && dbt test --profiles-dir .`
6. View the DAG in Airflow: http://localhost:8080 (user `admin`, password `admin`)

## What I learned / next steps

- Migrate the warehouse to BigQuery/Snowflake and raw data to an S3/GCS bucket.
- Incremental ingestion instead of a full replace.
- Add `dbt-expectations` for more advanced tests.
- Final dashboard (Metabase) on top of the `marts` models.
