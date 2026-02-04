from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.user import User
from ..models.order import Order, OrderStatus
from ..models.menu import MenuItem
from ..schemas.order import OrderResponse
from ..dependencies.auth import get_current_user, require_role
from ..websockets.manager import manager

router = APIRouter(prefix="/api/waiter", tags=["Waiter"])

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
async def get_ready_orders(
    current_user: User = Depends(require_role(["waiter", "admin"])),
    db: Session = Depends(get_db)
):
    """Get all orders ready to serve"""
    orders = db.query(Order).filter(
        Order.status == OrderStatus.READY_TO_SERVE
    ).order_by(Order.created_at).all()
    
    return [format_order_response(order, db) for order in orders]

@router.put("/orders/{order_id}/serve")
async def mark_order_served(
    order_id: int,
    current_user: User = Depends(require_role(["waiter", "admin"])),
    db: Session = Depends(get_db)
):
    """Mark order as served"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.status != OrderStatus.READY_TO_SERVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order is not ready to serve"
        )
    
    order.status = OrderStatus.SERVED
    db.commit()
    db.refresh(order)
    
    order_response = format_order_response(order, db)
    
    await manager.notify_order_update(
        order.id,
        order.user_id,
        OrderStatus.SERVED.value,
        order_response
    )
    
    return order_response

@router.get("/orders/all", response_model=List[OrderResponse])
async def get_all_active_orders(
    current_user: User = Depends(require_role(["waiter", "admin"])),
    db: Session = Depends(get_db)
):
    """Get all active orders (not served)"""
    orders = db.query(Order).filter(
        Order.status != OrderStatus.SERVED
    ).order_by(Order.created_at).all()
    
    return [format_order_response(order, db) for order in orders]