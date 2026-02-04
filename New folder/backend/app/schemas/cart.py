from pydantic import BaseModel
from typing import List
from decimal import Decimal

class CartItemBase(BaseModel):
    item_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    item_id: int
    quantity: int
    price: Decimal
    item_name: str
    item_description: str
    
    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse]
    total: Decimal
    
    class Config:
        from_attributes = True