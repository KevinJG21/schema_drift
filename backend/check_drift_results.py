from app.database.database import SessionLocal
from app.models.dataset import Dataset
from app.models.schema_version import SchemaVersion
from app.models.drift_result import DriftResult

db = SessionLocal()

results = db.query(DriftResult).all()

for result in results:
    print(
        "Dataset ID:", result.dataset_id,
        "| Version ID:", result.schema_version_id,
        "| Change:", result.change_type,
        "| Column:", result.column_name,
        "| Severity:", result.severity,
        "| Details:", result.details
    )

db.close()