from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class ExperimentFile(Base):
    __tablename__ = "experiment_file"

    id_experiment = Column(
        Integer,
        ForeignKey("experiment.id_experiment", ondelete="CASCADE"),
        primary_key=True
    )
    id_file = Column(
        Integer,
        ForeignKey("file.id_file", ondelete="CASCADE"),
        primary_key=True
    )

    experiment = relationship("Experiment", back_populates="files")
    file = relationship("File")