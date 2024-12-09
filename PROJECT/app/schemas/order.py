from pydantic import BaseModel, Field
from typing import Optional

class OrderCreate(BaseModel):
    product_id: int
    quantity: int
    offer_code: Optional[str] = None  # Offers are optional

    class Config:
        orm_mode = True

class OrderUpdate(BaseModel):
    product_id : int
    quantity : int

    class Config:
        orm_mode = True
    

class OrderResponse(BaseModel):
    order_id: int
    user_id: int
    product_id: int
    total_amount: float
    discount_amount: float
    final_amount: float
    created_at: str

    class Config:
        orm_mode = True
