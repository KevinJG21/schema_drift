from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

import pendulum
import sys


sys.path.append("/opt/airflow/backend")

def run_schema_drift():
    from app.database.database import SessionLocal
    from app.services.schema_version_service import process_dataset

    db = SessionLocal()

    try:
        result = process_dataset(
            db=db,
            dataset_name="customers",
            file_path = "/opt/airflow/backend/uploads/test_customers_v3.csv"
        )

        print("Schema drift check completed!")
        print(result)

    finally:
        db.close()    


with DAG(
    dag_id="hello_schema_drift",
    start_date=pendulum.datetime(
        2026,
        9,
        4,
        tz="Asia/Kolkata"
    ),
    schedule=None,
    catchup=False,
) as dag:

    schema_drift_task = PythonOperator(
    task_id="run_schema_drift",
    python_callable=run_schema_drift,
)