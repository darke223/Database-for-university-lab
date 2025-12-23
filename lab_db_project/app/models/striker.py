from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base

class Striker(Base):
    __tablename__ = "striker"

    id_striker = Column(Integer, primary_key=True)
    material = Column(String(255), nullable=False)
    geometric_dimensions = Column(JSONB, nullable=False)

    experiments = relationship("Experiment", back_populates="striker")