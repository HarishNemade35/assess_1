from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.core.db import Base
from datetime import datetime

class Offer(Base):
    __tablename__ = "offers"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    discount_value = Column(Float, nullable=False)  # Flat discount amount or percentage
    is_percentage = Column(Boolean, nullable=False)  # True if percentage, False if flat
    expiry_date = Column(DateTime, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)  # Optional, for product-specific offers
    
    # Relationships
    product = relationship("Product", back_populates="offers")
    owner_id = Column(Integer, ForeignKey("owners.id"))
    owner = relationship("Owner", back_populates="offers")

