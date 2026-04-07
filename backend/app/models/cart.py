from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional
from .base import PyObjectId

class CartItem(BaseModel):
    menu_item_id: str
    name: str
    price: float
    quantity: int = Field(default=1, ge=1)
    image_url: Optional[str] = None

class Cart(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    items: List[CartItem] = []
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )