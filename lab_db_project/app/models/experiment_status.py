from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class ExperimentStatus(Base):
    __tablename__ = "experiment_status"

    id_status = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    experiments = relationship("Experiment", back_populates="status")