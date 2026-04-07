from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from typing import List
from ..database import get_db
from ..models.user import User
from ..schemas.order import OrderResponse
from ..dependencies.auth import require_role
from ..websockets.manager import manager
from datetime import datetime

router = APIRouter(prefix="/api/waiter", tags=["Waiter"])

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
async def get_ready_orders(
    current_user: User = Depends(require_role(["waiter", "admin"])),
    db = Depends(get_db)
):
    """Get all orders ready to serve"""
    cursor = db.orders.find({"status": "Ready to Serve"}).sort("created_at", 1)
    orders = []
    async for doc in cursor:
        orders.append(format_order_response(doc))
    return orders

@router.put("/orders/{order_id}/serve")
async def mark_order_served(
    order_id: str,
    current_user: User = Depends(require_role(["waiter", "admin"])),
    db = Depends(get_db)
):
    """Mark order as served"""
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order ID")
        
    obj_id = ObjectId(order_id)
    order_doc = await db.orders.find_one({"_id": obj_id})
    if not order_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
    if order_doc.get("status") != "Ready to Serve":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is not ready to serve")
        
    await db.orders.update_one(
        {"_id": obj_id}, 
        {"$set": {"status": "Served", "updated_at": datetime.utcnow()}}
    )
    
    updated_order_doc = await db.orders.find_one({"_id": obj_id})
    order_response = format_order_response(updated_order_doc)
    
    await manager.notify_order_update(
        str(updated_order_doc["_id"]),
        str(updated_order_doc.get("user_id")),
        "Served",
        order_response
    )
    
    return order_response

@router.get("/orders/all", response_model=List[OrderResponse])
async def get_all_active_orders(
    current_user: User = Depends(require_role(["waiter", "admin"])),
    db = Depends(get_db)
):
    """Get all active orders (not served)"""
    cursor = db.orders.find({"status": {"$ne": "Served"}}).sort("created_at", 1)
    orders = []
    async for doc in cursor:
        orders.append(format_order_response(doc))
    return orders