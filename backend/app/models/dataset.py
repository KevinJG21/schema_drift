from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Dataset(Base):   #here, using Base has made this class a sqlalchemy model.
    __tablename__ = "datasets"

    id = Column(
        Integer,       #these are columns of the table ie. id, name and created_at.
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    schema_versions = relationship("SchemaVersion", back_populates="dataset")


    #SQLAlchemy also contains the blueprint/definition for the table in the database.
    #Acts as the bridge between SQL and Python. 
    