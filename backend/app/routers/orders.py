from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from typing import List
from datetime import datetime
from ..database import get_db
from ..models.user import User
from ..schemas.order import OrderCreate, OrderResponse, PaymentRequest
from ..dependencies.auth import get_current_user
from ..websockets.manager import manager

router = APIRouter(prefix="/api/orders", tags=["Orders"])

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

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    user_id_str = str(current_user.id)
    cart = await db.carts.find_one({"user_id": user_id_str})
    if not cart or not cart.get("items"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    
    items = cart.get("items", [])
    total = sum([item.get("price", 0.0) * item.get("quantity", 1) for item in items])
    
    order_items = []
    for item in items:
        order_items.append({
            "item_id": item.get("menu_item_id"),
            "name": item.get("name", "Unknown"),
            "price": item.get("price", 0.0),
            "quantity": item.get("quantity", 1),
            "image_url": item.get("image_url", None)
        })
        
    order_doc = {
        "user_id": user_id_str,
        "total_price": total,
        "status": "Placed",
        "payment_status": "Pending",
        "notes": order_data.notes,
        "table_number": order_data.table_number,
        "items": order_items,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.orders.insert_one(order_doc)
    order_doc["_id"] = result.inserted_id
    
    # Clear cart
    await db.carts.update_one({"_id": cart["_id"]}, {"$set": {"items": [], "updated_at": datetime.utcnow()}})
    
    response = format_order_response(order_doc)
    await manager.notify_order_update(
        str(result.inserted_id),
        user_id_str,
        "Placed",
        response
    )
    
    return response

@router.get("/", response_model=List[OrderResponse])
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    user_id_str = str(current_user.id)
    cursor = db.orders.find({"user_id": user_id_str}).sort("created_at", -1)
    orders = []
    async for order_doc in cursor:
        orders.append(format_order_response(order_doc))
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order ID")
        
    obj_id = ObjectId(order_id)
    order_doc = await db.orders.find_one({"_id": obj_id})
    if not order_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    user_id_str = str(current_user.id)
    if str(order_doc.get("user_id")) != user_id_str and current_user.role not in ["waiter", "kitchen", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
    return format_order_response(order_doc)

@router.post("/{order_id}/payment")
async def process_payment(
    order_id: str,
    payment: PaymentRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order ID")
        
    obj_id = ObjectId(order_id)
    order_doc = await db.orders.find_one({"_id": obj_id})
    if not order_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
    user_id_str = str(current_user.id)
    if str(order_doc.get("user_id")) != user_id_str:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
    if order_doc.get("payment_status") == "Completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order already paid")
        
    await db.orders.update_one({"_id": obj_id}, {"$set": {"payment_status": "Completed", "updated_at": datetime.utcnow()}})
    
    return {
        "message": "Payment processed successfully",
        "order_id": order_id,
        "payment_status": "Completed"
    }
