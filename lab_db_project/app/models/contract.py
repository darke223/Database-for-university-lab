from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base

class Contract(Base):
    __tablename__ = "contract"

    id_contract = Column(Integer, primary_key=True)
    id_customer = Column(Integer, ForeignKey("customer.id_customer"))
    start_date = Column(Date)
    end_date = Column(Date)

    customer = relationship("Customer", back_populates="contracts")
    experiments = relationship("Experiment", back_populates="contract")