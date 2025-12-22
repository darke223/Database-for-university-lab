from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base

class Customer(Base):
    __tablename__ = "customer"

    id_customer = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    email = Column(String(100))
    phone = Column(String(30))

    contracts = relationship("Contract", back_populates="customer")