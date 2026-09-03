from app.database.database import SessionLocal
from app.models.dataset import Dataset
from app.models.schema_version import SchemaVersion


db = SessionLocal()

dataset = db.query(Dataset).filter(
    Dataset.name == "customers"
).first()

versions = db.query(SchemaVersion).filter(
    SchemaVersion.dataset_id == dataset.id
).all()

for version in versions:
    print(
        version.version_number,
        version.schema_json
    )

db.close()