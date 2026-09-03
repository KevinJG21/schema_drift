from pydantic import BaseModel
from typing import Any


class DriftChange(BaseModel):
    column: str
    change_type: str
    severity: str
    old_value: Any | None = None
    new_value: Any | None = None


class DriftResponse(BaseModel):
    has_drift: bool
    changes: list[DriftChange]


class DatasetCheckResponse(BaseModel):
    dataset: str
    version: int
    drift: DriftResponse


class DatasetResponse(BaseModel):
    id: int
    name: str

class SchemaVersionResponse(BaseModel):
    id: int
    version_number: int
    schema_json: dict

class DriftResultResponse(BaseModel):
    id: int
    schema_version_id: int
    change_type: str
    column_name: str
    severity: str
    details: dict | None = None

    