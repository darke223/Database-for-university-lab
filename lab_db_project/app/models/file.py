from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy.sql import func

class File(Base):
    __tablename__ = "file"

    id_file = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(Text, nullable=False)
    file_type = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Осциллограммы для результатов
    oscillogram_results = relationship("Result", back_populates="oscillogram_file")
    # Многие-ко-многим с экспериментами
    experiments = relationship("Experiment", secondary="experiment_file", back_populates="files")