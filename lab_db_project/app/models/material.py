from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base

class Material(Base):
    __tablename__ = "material"

    id_material = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    description = Column(Text)

    samples = relationship("Sample", back_populates="material")