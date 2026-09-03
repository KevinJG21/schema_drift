from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class DriftResult(Base):
    __tablename__ = "drift_results"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    dataset_id = Column(
        Integer,
        ForeignKey("datasets.id"),
        nullable=False
    )

    schema_version_id = Column(
        Integer,
        ForeignKey("schema_versions.id"),
        nullable=False
    )

    change_type = Column(
        String,
        nullable=False
    )

    column_name = Column(
        String,
        nullable=False
    )

    severity = Column(
        String,
        nullable=False
    )

    details = Column(
        JSON,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    dataset = relationship(
        "Dataset"
    )

    schema_version = relationship(
        "SchemaVersion"
    )