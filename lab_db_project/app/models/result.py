from sqlalchemy import Column, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base

class Result(Base):
    __tablename__ = "result"

    id_result = Column(Integer, primary_key=True, autoincrement=True)
    measurements = Column(JSONB)
    id_oscillogram_file = Column(Integer, ForeignKey("file.id_file", ondelete="SET NULL"))

    oscillogram_file = relationship("File", back_populates="oscillogram_results")
    experiment = relationship("Experiment", back_populates="result")

    __table_args__ = (
        Index('ix_result_measurements_gin', 'measurements', postgresql_using='gin'),
    )