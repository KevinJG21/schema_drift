from pathlib import Path

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.dataset import Dataset
from app.models.schema_version import SchemaVersion
from app.models.drift_result import DriftResult
from app.services.schema_version_service import process_dataset
from app.schemas.drift import (
    DatasetCheckResponse,
    DatasetResponse,
    SchemaVersionResponse,
    DriftResultResponse
)


app = FastAPI(
    title="Schema Drift Intelligence Platform",
    version="1.0.0"
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "message": "Schema Drift Platform Running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

@app.post(
    "/datasets/{dataset_name}/check",
    response_model=DatasetCheckResponse
)
def check_dataset(
    dataset_name: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No file was uploaded."
            )

        if not file.filename.lower().endswith(".csv"):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are supported."
            )

        dataset_name = Path(dataset_name).name

        if not dataset_name or dataset_name in {".", ".."}:
            raise HTTPException(
                status_code=400,
                detail="Invalid dataset name."
            )

        file_path = Path("uploads") / f"{dataset_name}.csv"

        upload_dir = file_path.parent
        upload_dir.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        result = process_dataset(
            db,
            dataset_name,
            file_path
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the dataset."
        )
@app.get(
    "/datasets",
    response_model=list[DatasetResponse]
)
def get_datasets(
    db: Session = Depends(get_db)
):
    datasets = db.query(Dataset).all()

    return datasets

@app.get(
    "/datasets/{dataset_name}/versions",
    response_model=list[SchemaVersionResponse]
)
def get_schema_versions(
    dataset_name: str,
    db: Session = Depends(get_db)
):
    dataset = db.query(Dataset).filter(
        Dataset.name == dataset_name
    ).first()

    if dataset is None:
        return []

    versions = db.query(SchemaVersion).filter(
        SchemaVersion.dataset_id == dataset.id
    ).order_by(
        SchemaVersion.version_number.asc()
    ).all()

    return versions

@app.get(
    "/datasets/{dataset_name}/drifts",
    response_model=list[DriftResultResponse]
)
def get_drift_results(
    dataset_name: str,
    db: Session = Depends(get_db)
):
    dataset = db.query(Dataset).filter(
        Dataset.name == dataset_name
    ).first()

    if dataset is None:
        return []

    results = db.query(DriftResult).filter(
        DriftResult.dataset_id == dataset.id
    ).order_by(
        DriftResult.id.asc()
    ).all()

    return results