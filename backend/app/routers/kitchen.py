from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from typing import List
from ..database import get_db
from ..models.user import User
from ..schemas.order import OrderResponse, OrderStatusUpdate
from ..dependencies.auth import require_role
from ..websockets.manager import manager
from datetime import datetime

router = APIRouter(prefix="/api/kitchen", tags=["Kitchen"])

def format_order_response(order_doc: dict) -> dict:
    items = []
    for item in order_doc.get("items", []):
        items.append({
            "item_id": str(item.get("item_id")),
            "quantity": item.get("quantity", 1),
            "price": float(item.get("price", 0.0)),
            "item_name": item.get("name", "Unknown"),
            "image_url": item.get("image_url", None)
        })
    
    return {
        "id": str(order_doc["_id"]),
        "user_id": str(order_doc.get("user_id")),
        "total_price": float(order_doc.get("total_price", 0.0)),
        "status": order_doc.get("status", "Placed"),
        "payment_status": order_doc.get("payment_status", "Pending"),
        "notes": order_doc.get("notes"),
        "table_number": order_doc.get("table_number"),
        "items": items,
        "created_at": order_doc.get("created_at"),
        "updated_at": order_doc.get("updated_at")
    }

@router.get("/orders", response_model=List[OrderResponse])
async def get_pending_orders(
    current_user: User = Depends(require_role(["kitchen", "admin"])),
    db = Depends(get_db)
):
    """Get all orders that need kitchen attention"""
    cursor = db.orders.find({
        "status": {"$in": ["Placed", "Preparing", "Cooking"]}
    }).sort("created_at", 1)
    
    orders = []
    async for order_doc in cursor:
        orders.append(format_order_response(order_doc))
        
    return orders

@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(require_role(["kitchen", "admin"])),
    db = Depends(get_db)
):
    """Update order status in kitchen workflow"""
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order ID")
        
    obj_id = ObjectId(order_id)
    order_doc = await db.orders.find_one({"_id": obj_id})
    if not order_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    valid_statuses = ["Placed", "Preparing", "Cooking", "Ready to Serve"]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    update_data = {
        "status": status_update.status,
        "updated_at": datetime.utcnow()
    }
    if status_update.notes is not None:
        update_data["notes"] = status_update.notes
        
    await db.orders.update_one({"_id": obj_id}, {"$set": update_data})
    
    # Reload to get updated doc
    updated_order_doc = await db.orders.find_one({"_id": obj_id})
    order_response = format_order_response(updated_order_doc)
    
    await manager.notify_order_update(
        str(updated_order_doc["_id"]),
        str(updated_order_doc.get("user_id")),
        status_update.status,
        order_response
    )
    
    return order_response