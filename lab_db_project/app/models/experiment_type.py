from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class ExperimentType(Base):
    __tablename__ = "experiment_type"

    experiment_type_code = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    experiments = relationship("Experiment", back_populates="experiment_type")