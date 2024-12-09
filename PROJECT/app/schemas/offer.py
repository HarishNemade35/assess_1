from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class OfferBase(BaseModel):
    code: str = Field(..., min_length=3, max_length=20)
    discount_value: float
    is_percentage: bool
    expiry_date: datetime  # Use timezone-aware datetime
    product_id: int

class OfferCreate(OfferBase):
    pass


class OfferUpdate(OfferBase):
    code:str =Field(..., min_length=3, max_length=20)
    discount_value :float
    is_percentage : bool
    expiry_date : datetime
    product_id : int

class OfferResponse(OfferBase):
    id: int
    product_id: Optional[int]

    class Config:
        orm_mode = True
