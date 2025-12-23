# app/models/contract.py
from sqlalchemy import Column, Integer, Date, Text, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Contract(Base):
    __tablename__ = "contract"

    id_contract = Column(Integer, primary_key=True)
    id_customer = Column(Integer, ForeignKey("customer.id_customer"), nullable=False)

    date_of_sample_delivery = Column(Date, nullable=False)
    delivery_type = Column(String(50), nullable=False)
    technical_specification = Column(Text)
    materials_to_study = Column(Text)
    report = Column(Text)
    contract_document = Column(Text)

    customer = relationship("Customer", back_populates="contracts")
    experiments = relationship("Experiment", back_populates="contract")