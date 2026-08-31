from sqlalchemy import Column, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class SchemaVersion(Base):    #same goes here, it has become a sqlalchemy model. 
    __tablename__ = "schema_versions"

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

    version_number = Column(
        Integer,
        nullable=False
    )

    schema_json = Column(
        JSON,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    dataset = relationship(
        "Dataset",
        back_populates="schema_versions"
    )