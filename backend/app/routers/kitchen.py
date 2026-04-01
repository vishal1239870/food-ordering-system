from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.user import User
from ..models.order import Order, OrderStatus
from ..models.menu import MenuItem
from ..schemas.order import OrderResponse, OrderStatusUpdate
from ..dependencies.auth import get_current_user, require_role
from ..websockets.manager import manager

router = APIRouter(prefix="/api/kitchen", tags=["Kitchen"])

def format_order_response(order: Order, db: Session) -> dict:
    """Helper to format order with items"""
    items = []
    for order_item in order.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == order_item.item_id).first()
        items.append({
            "id": order_item.id,
            "item_id": order_item.item_id,
            "quantity": order_item.quantity,
            "price": order_item.price,
            "item_name": menu_item.name if menu_item else "Unknown"
        })
    
    return {
        "id": order.id,
        "user_id": order.user_id,
        "total_price": order.total_price,
        "status": order.status.value,
        "payment_status": order.payment_status.value,
        "notes": order.notes,
        "table_number": order.table_number,
        "items": items,
        "created_at": order.created_at,
        "updated_at": order.updated_at
    }

@router.get("/orders", response_model=List[OrderResponse])
async def get_pending_orders(
    current_user: User = Depends(require_role(["kitchen", "admin"])),
    db: Session = Depends(get_db)
):
    """Get all orders that need kitchen attention"""
    orders = db.query(Order).filter(
        Order.status.in_([
            OrderStatus.PLACED,
            OrderStatus.PREPARING,
            OrderStatus.COOKING
        ])
    ).order_by(Order.created_at).all()
    
    return [format_order_response(order, db) for order in orders]

@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(require_role(["kitchen", "admin"])),
    db: Session = Depends(get_db)
):
    """Update order status in kitchen workflow"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Validate status transition
    valid_statuses = [
        OrderStatus.PLACED.value,
        OrderStatus.PREPARING.value,
        OrderStatus.COOKING.value,
        OrderStatus.READY_TO_SERVE.value
    ]
    
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    # Update order
    order.status = OrderStatus(status_update.status)
    if status_update.notes:
        order.notes = status_update.notes
    
    db.commit()
    db.refresh(order)
    
    # Format response
    order_response = format_order_response(order, db)
    
    # Notify via WebSocket
    await manager.notify_order_update(
        order.id,
        order.user_id,
        status_update.status,
        order_response
    )
    
    return order_response