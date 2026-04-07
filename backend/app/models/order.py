from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional
from enum import Enum
from .base import PyObjectId

class OrderStatus(str, Enum):
    PLACED = "Placed"
    PREPARING = "Preparing"
    COOKING = "Cooking"
    READY_TO_SERVE = "Ready to Serve"
    SERVED = "Served"
    CANCELLED = "Cancelled"

class OrderItem(BaseModel):
    menu_item_id: str
    name: str
    price: float
    quantity: int = Field(default=1, ge=1)
    image_url: Optional[str] = None

class Order(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    status: OrderStatus = OrderStatus.PLACED
    total_price: float = Field(..., ge=0)
    items: List[OrderItem]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )