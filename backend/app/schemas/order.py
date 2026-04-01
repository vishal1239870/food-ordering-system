from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class OrderItemBase(BaseModel):
    item_id: int
    quantity: int
    price: Decimal

class OrderItemResponse(BaseModel):
    id: int
    item_id: int
    quantity: int
    price: Decimal
    item_name: str
    
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    notes: Optional[str] = None
    table_number: Optional[int] = None

class OrderStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: Decimal
    status: str
    payment_status: str
    notes: Optional[str]
    table_number: Optional[int]
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PaymentRequest(BaseModel):
    payment_method: str = "card"
