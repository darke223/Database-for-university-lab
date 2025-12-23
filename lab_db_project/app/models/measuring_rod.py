from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base

class MeasuringRod(Base):
    __tablename__ = "measuring_rod"

    id_rod = Column(Integer, primary_key=True)
    material = Column(String(255), nullable=False)
    geometric_dimensions = Column(JSONB, nullable=False)
    physical_properties = Column(JSONB, nullable=False)