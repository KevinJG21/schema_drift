from app.database.database import SessionLocal
from app.models.dataset import Dataset
from app.models.schema_version import SchemaVersion

from app.database.database import SessionLocal
from app.models.dataset import Dataset
from app.models.schema_version import SchemaVersion

from app.services.schema_capture import capture_schema

from app.services.schema_comparator import compare_schemas
from app.models.drift_result import DriftResult



def get_or_create_dataset(db, dataset_name):

    dataset = db.query(Dataset).filter(
        Dataset.name == dataset_name
    ).first()

    if dataset is None:

        dataset = Dataset(name=dataset_name)

        db.add(dataset)
        db.commit()
        db.refresh(dataset)

    return dataset

def create_schema_version(db, dataset, schema):

    latest_version = db.query(SchemaVersion).filter(
        SchemaVersion.dataset_id == dataset.id
    ).order_by(
        SchemaVersion.version_number.desc()
    ).first()

    if latest_version is None:
        next_version = 1
    else:
        next_version = latest_version.version_number + 1

    schema_version = SchemaVersion(
        dataset_id=dataset.id,
        version_number=next_version,
        schema_json=schema
    )

    db.add(schema_version)
    db.commit()
    db.refresh(schema_version)

    return schema_version

def get_latest_schema(db, dataset_id):

    latest_version = db.query(SchemaVersion).filter(
        SchemaVersion.dataset_id == dataset_id
    ).order_by(
        SchemaVersion.version_number.desc()
    ).first()

    if latest_version is None:
        return None

    return latest_version.schema_json

def process_dataset(db, dataset_name, file_path):

    dataset = get_or_create_dataset(
        db,
        dataset_name
    )

    old_schema = get_latest_schema(
        db,
        dataset.id
    )

    new_schema = capture_schema(
        file_path
    )

    if old_schema is None:
        drift_result = {
            "has_drift": False,
            "changes": []
        }
    else:
        drift_result = compare_schemas(
            old_schema,
            new_schema
        )

    version = create_schema_version(
        db,
        dataset,
        new_schema
    )

    for change in drift_result["changes"]:

        drift = DriftResult(
            dataset_id=dataset.id,
            schema_version_id=version.id,
            change_type=change["change_type"],
            column_name=change["column"],
            severity=change["severity"],
            details={
                "old_value": change.get("old_value"),
                "new_value": change.get("new_value")
            }
        )

        db.add(drift)

    db.commit()

    return {
        "dataset": dataset.name,
        "version": version.version_number,
        "drift": drift_result
    }

if __name__ == "__main__":
    db = SessionLocal()

    result = process_dataset(
        db,
        "customers",
        "uploads/test_customers_v6.csv"
    )

    print(result)

    db.close()