from pydantic import BaseModel
from typing import List, Optional
from app.schemas.offer import OfferResponse
class ProductBase(BaseModel):
    name: str
    price: float
    stock: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    class Config:
        orm_mode = True

class ProductWithOffers(ProductResponse):
    offers: Optional[List["OfferResponse"]] = []

    class Config:
        orm_mode = True
