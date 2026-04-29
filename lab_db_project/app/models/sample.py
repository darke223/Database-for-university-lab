from sqlalchemy import Column, Integer, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base

class Sample(Base):
    __tablename__ = "sample"

    id_sample = Column(Integer, primary_key=True)
    id_material = Column(Integer, ForeignKey("material.id_material"), nullable=False)

    geometry = Column(JSONB)
    physical_properties = Column(JSONB)
    description = Column(Text)

    material = relationship("Material", back_populates="samples")
    experiments = relationship("Experiment", back_populates="sample")

    __table_args__ = (
        Index('ix_sample_geometry_gin', 'geometry', postgresql_using='gin'),
        Index('ix_sample_phys_props_gin', 'physical_properties', postgresql_using='gin'),
    )



