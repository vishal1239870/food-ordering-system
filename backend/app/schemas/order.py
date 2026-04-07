from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OrderItemBase(BaseModel):
    item_id: str
    quantity: int
    price: float

class OrderItemResponse(BaseModel):
    item_id: str
    quantity: int
    price: float
    item_name: str
    image_url: Optional[str] = None

class OrderCreate(BaseModel):
    notes: Optional[str] = None
    table_number: Optional[int] = None

class OrderStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class OrderResponse(BaseModel):
    id: str
    user_id: str
    total_price: float
    status: str
    payment_status: str
    notes: Optional[str] = None
    table_number: Optional[int] = None
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

class PaymentRequest(BaseModel):
    payment_method: str = "card"
