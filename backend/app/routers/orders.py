from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from ..database import get_db
from ..models.user import User
from ..models.order import Order, OrderItem, OrderStatus, PaymentStatus
from ..models.cart import Cart, CartItem
from ..models.menu import MenuItem
from ..schemas.order import OrderCreate, OrderResponse, OrderItemResponse, PaymentRequest
from ..dependencies.auth import get_current_user
from ..websockets.manager import manager

router = APIRouter(prefix="/api/orders", tags=["Orders"])

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

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create order from cart"""
    # Get user's cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    
    # Calculate total
    total = Decimal("0.00")
    for item in cart.items:
        total += item.price * item.quantity
    
    # Create order
    new_order = Order(
        user_id=current_user.id,
        total_price=total,
        status=OrderStatus.PLACED,
        payment_status=PaymentStatus.PENDING,
        notes=order_data.notes,
        table_number=order_data.table_number
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # Create order items from cart
    for cart_item in cart.items:
        order_item = OrderItem(
            order_id=new_order.id,
            item_id=cart_item.item_id,
            quantity=cart_item.quantity,
            price=cart_item.price
        )
        db.add(order_item)
    
    # Clear cart
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    
    # Format response
    order_response = format_order_response(new_order, db)
    
    # Notify via WebSocket
    await manager.notify_order_update(
        new_order.id,
        current_user.id,
        OrderStatus.PLACED.value,
        order_response
    )
    
    return order_response

@router.get("/", response_model=List[OrderResponse])
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all orders for current user"""
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(Order.created_at.desc()).all()
    
    return [format_order_response(order, db) for order in orders]

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if user owns the order (or is staff)
    if order.user_id != current_user.id and current_user.role not in ["waiter", "kitchen", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return format_order_response(order, db)

@router.post("/{order_id}/payment")
async def process_payment(
    order_id: int,
    payment: PaymentRequest,  # now only expects payment_method
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process payment for order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if order.payment_status == PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already paid"
        )
    
    # Process payment (dummy)
    order.payment_status = PaymentStatus.COMPLETED
    db.commit()
    
    return {
        "message": "Payment processed successfully",
        "order_id": order_id,
        "payment_status": "completed"
    }
