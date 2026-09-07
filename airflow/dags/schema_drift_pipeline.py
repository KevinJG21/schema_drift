from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

import pendulum
import sys
from pathlib import Path


sys.path.append("/opt/airflow/backend")


def get_datasets_and_files():

    from app.database.database import SessionLocal
    from app.services.schema_version_service import get_dataset_files

    db = SessionLocal()

    try:
        return get_dataset_files(db)

    finally:
        db.close()


def run_schema_drift(dataset_name, file_path):

    if not Path(file_path).exists():
        raise FileNotFoundError(
            f"CSV file not found for dataset '{dataset_name}': {file_path}"
        )

    from app.database.database import SessionLocal
    from app.services.schema_version_service import process_dataset

    db = SessionLocal()

    try:
        result = process_dataset(
            db=db,
            dataset_name=dataset_name,
            file_path=file_path
        )

        print("Schema drift check completed!")
        print(result)

    finally:
        db.close()


with DAG(
    dag_id="schema_drift_pipeline",
    start_date=pendulum.datetime(
        2026,
        9,
        4,
        tz="Asia/Kolkata"
    ),
    schedule="0 9 * * *",
    catchup=False,
) as dag:

    datasets = get_datasets_and_files()

    for dataset in datasets:

        dataset_name = dataset["dataset_name"]

        file_path = (
            "/opt/airflow/backend/"
            + dataset["file_path"]
        )

        PythonOperator(
            task_id=f"check_{dataset_name}",
            python_callable=run_schema_drift,
            op_kwargs={
                "dataset_name": dataset_name,
                "file_path": file_path
            }
        )