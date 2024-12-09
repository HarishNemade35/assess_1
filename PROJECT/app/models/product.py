from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey("owners.id"),nullable=False)# Foreign key to Owner
    
    # Relationship with offers
    owner = relationship("Owner", back_populates="products")
    offers = relationship("Offer", back_populates="product")
    orders = relationship("Order", back_populates="product")
