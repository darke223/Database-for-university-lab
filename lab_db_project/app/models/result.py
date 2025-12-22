from sqlalchemy import Column, Integer, Float, ForeignKey, Text, String
from sqlalchemy.orm import relationship

from .base import Base

class Result(Base):
    __tablename__ = "result"

    id_result = Column(Integer, primary_key=True)
    id_experiment = Column(Integer, ForeignKey("experiment.id_experiment"))

    value = Column(Float)
    unit = Column(String(20))
    comment = Column(Text)

    experiment = relationship("Experiment", back_populates="results")