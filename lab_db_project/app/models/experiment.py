from sqlalchemy import Column, Integer, Date, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base


class Experiment(Base):
    __tablename__ = "experiment"

    id_experiment = Column(Integer, primary_key=True, autoincrement=True)

    id_sample = Column(Integer, ForeignKey("sample.id_sample", ondelete="RESTRICT"), nullable=False)
    experiment_type_code = Column(Integer, ForeignKey("experiment_type.experiment_type_code", ondelete="RESTRICT"),
                                  nullable=False)
    id_status = Column(Integer, ForeignKey("experiment_status.id_status", ondelete="RESTRICT"), nullable=False)
    id_striker = Column(Integer, ForeignKey("striker.id_striker", ondelete="RESTRICT"), nullable=False)
    loading_rod_id = Column(Integer, ForeignKey("measuring_rod.id_rod", ondelete="RESTRICT"), nullable=False)
    support_rod_id = Column(Integer, ForeignKey("measuring_rod.id_rod", ondelete="RESTRICT"), nullable=False)
    id_contract = Column(Integer, ForeignKey("contract.id_contract", ondelete="RESTRICT"), nullable=False)
    experiment_date = Column(Date, nullable=False)
    comments = Column(Text)
    id_result = Column(Integer, ForeignKey("result.id_result", ondelete="CASCADE"), unique=True, nullable=True)

    # Отношения (исправлено: используем строки с именами колонок)
    sample = relationship("Sample", back_populates="experiments")
    experiment_type = relationship("ExperimentType", back_populates="experiments")
    status = relationship("ExperimentStatus", back_populates="experiments")
    striker = relationship("Striker", back_populates="experiments")

    loading_rod = relationship(
        "MeasuringRod",
        foreign_keys="Experiment.loading_rod_id",  # строка с именем таблицы и колонки
        back_populates="loading_experiments"
    )
    support_rod = relationship(
        "MeasuringRod",
        foreign_keys="Experiment.support_rod_id",
        back_populates="support_experiments"
    )

    contract = relationship("Contract", back_populates="experiments")
    result = relationship("Result", back_populates="experiment", uselist=False)
    files = relationship("File", secondary="experiment_file", back_populates="experiments")