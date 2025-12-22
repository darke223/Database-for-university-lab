from sqlalchemy import Column, Integer, Date, ForeignKey, String
from sqlalchemy.orm import relationship

from .base import Base

class Experiment(Base):
    __tablename__ = "experiment"

    id_experiment = Column(Integer, primary_key=True)
    id_sample = Column(Integer, ForeignKey("sample.id_sample"))
    id_contract = Column(Integer, ForeignKey("contract.id_contract"))

    date_start = Column(Date)
    status = Column(String(30))

    sample = relationship("Sample", back_populates="experiments")
    contract = relationship("Contract", back_populates="experiments")
    results = relationship("Result", back_populates="experiment")