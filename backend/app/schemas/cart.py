from pydantic import BaseModel
from typing import List
from decimal import Decimal

class CartItemBase(BaseModel):
    item_id: str
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    item_id: str
    quantity: int
    price: float
    item_name: str
    item_description: str

class CartResponse(BaseModel):
    id: str
    user_id: str
    items: List[CartItemResponse]
    total: float