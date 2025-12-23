from sqlalchemy import Column, Integer, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Experiment(Base):
    __tablename__ = "experiment"

    id_experiment = Column(Integer, primary_key=True)

    id_sample = Column(Integer, ForeignKey("sample.id_sample"), nullable=False)
    experiment_type_code = Column(Integer, ForeignKey("experiment_type.experiment_type_code"), nullable=False)
    id_status = Column(Integer, ForeignKey("experiment_status.id_status"), nullable=False)

    id_striker = Column(Integer, ForeignKey("striker.id_striker"), nullable=False)
    loading_rod_id = Column(Integer, ForeignKey("measuring_rod.id_rod"), nullable=False)
    support_rod_id = Column(Integer, ForeignKey("measuring_rod.id_rod"), nullable=False)

    id_contract = Column(Integer, ForeignKey("contract.id_contract"), nullable=False)
    experiment_date = Column(Date, nullable=False)

    comments = Column(Text)

    id_result = Column(Integer, ForeignKey("result.id_result", ondelete="CASCADE"), unique=True)

    sample = relationship("Sample", back_populates="experiments")
    experiment_type = relationship("ExperimentType", back_populates="experiments")
    status = relationship("ExperimentStatus", back_populates="experiments")
    striker = relationship("Striker", back_populates="experiments")
    contract = relationship("Contract", back_populates="experiments")
    result = relationship("Result", back_populates="experiment")
    files = relationship("ExperimentFile", back_populates="experiment")