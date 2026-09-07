# Schema Drift Intelligence Platform

A data engineering project for detecting and tracking schema changes in CSV datasets.

The system captures schemas, stores different schema versions in PostgreSQL, compares versions, and records schema drift. Apache Airflow is used for scheduled checks and Slack is used for high-severity alerts.

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pandas
- Streamlit
- Apache Airflow
- Docker
- Slack Webhooks

## Architecture

```mermaid
flowchart TD
    A[CSV] --> B[Streamlit]
    B --> C[FastAPI]
    C --> D[Schema Capture]
    D --> E[Schema Comparator]
    E --> F[(PostgreSQL)]

    F --> G[Schema Versions]
    F --> H[Drift Results]

    I[Apache Airflow] --> C
    E --> J{High Severity}
    J -->|Yes| K[Slack]