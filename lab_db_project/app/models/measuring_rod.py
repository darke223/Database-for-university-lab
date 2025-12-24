from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base

class MeasuringRod(Base):
    __tablename__ = "measuring_rod"

    id_rod = Column(Integer, primary_key=True, autoincrement=True)
    material = Column(String(255), nullable=False)
    geometric_dimensions = Column(JSONB, nullable=False)
    physical_properties = Column(JSONB, nullable=False)

    # Обратные связи
    loading_experiments = relationship("Experiment", foreign_keys="Experiment.loading_rod_id", back_populates="loading_rod")
    support_experiments = relationship("Experiment", foreign_keys="Experiment.support_rod_id", back_populates="support_rod")