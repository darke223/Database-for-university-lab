from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class Material(Base):
    __tablename__ = "material"

    id_material = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    samples = relationship("Sample", back_populates="material")