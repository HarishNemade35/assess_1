from sqlalchemy import Column, Integer, String
from app.core.db import Base
from sqlalchemy.orm import relationship

class Owner(Base):
    __tablename__ = "owners"
    
    id = Column(Integer, primary_key=True, index=True)
    ownername = Column(String, unique=True, index=True)
    # ownername = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    offers = relationship("Offer", back_populates="owner")
    products = relationship("Product", back_populates="owner")