from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta

from ..database import get_db
from ..models.user import User
from ..models.menu import MenuItem
from ..models.order import Order, OrderStatus, OrderItem
from ..schemas.menu import MenuItem as MenuItemSchema, MenuItemCreate, MenuItemUpdate
from ..dependencies.auth import require_role

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# ------------------------
# Menu Management
# ------------------------

@router.post("/menu", response_model=MenuItemSchema, status_code=status.HTTP_201_CREATED)
async def create_menu_item(
    item_data: MenuItemCreate,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Create new menu item including image_url"""
    new_item = MenuItem(**item_data.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.put("/menu/{item_id}", response_model=MenuItemSchema)
async def update_menu_item(
    item_id: int,
    item_data: MenuItemUpdate,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Update menu item including image_url"""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    update_data = item_data.dict(exclude_unset=True)

    # Update only provided fields
    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/menu/{item_id}")
async def delete_menu_item(
    item_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Delete menu item"""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    db.delete(item)
    db.commit()
    return {"message": "Menu item deleted successfully"}


@router.put("/menu/{item_id}/toggle")
async def toggle_menu_item_availability(
    item_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Toggle availability"""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    item.available = not item.available
    db.commit()
    db.refresh(item)
    return item


# ------------------------
# Analytics
# ------------------------

@router.get("/analytics/overview")
async def get_analytics_overview(
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Dashboard analytics"""
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    today_orders = db.query(Order).filter(func.date(Order.created_at) == today).all()
    today_revenue = sum(order.total_price for order in today_orders)

    active_orders = db.query(Order).filter(Order.status != OrderStatus.SERVED).count()

    week_orders = db.query(Order).filter(Order.created_at >= week_ago).all()
    week_revenue = sum(order.total_price for order in week_orders)

    month_orders = db.query(Order).filter(Order.created_at >= month_ago).all()
    month_revenue = sum(order.total_price for order in month_orders)

    status_breakdown = {
        status.value: db.query(Order).filter(Order.status == status).count()
        for status in OrderStatus
    }

    popular_items = db.query(
        MenuItem.name,
        func.sum(OrderItem.quantity).label("total_quantity")
    ).join(
        OrderItem, MenuItem.id == OrderItem.item_id
    ).group_by(
        MenuItem.id
    ).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(10).all()

    return {
        "today": {
            "revenue": float(today_revenue),
            "orders": len(today_orders),
            "active_orders": active_orders,
        },
        "week": {
            "revenue": float(week_revenue),
            "orders": len(week_orders),
        },
        "month": {
            "revenue": float(month_revenue),
            "orders": len(month_orders),
        },
        "status_breakdown": status_breakdown,
        "popular_items": [
            {"name": name, "quantity": int(qty)} for name, qty in popular_items
        ],
    }


@router.get("/analytics/orders")
async def get_orders_analytics(
    days: int = 7,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Analytics for last N days"""
    start_date = datetime.now() - timedelta(days=days)

    orders = (
        db.query(Order)
        .filter(Order.created_at >= start_date)
        .order_by(Order.created_at.desc())
        .all()
    )

    daily_stats = {}

    for order in orders:
        date_key = order.created_at.date().isoformat()

        if date_key not in daily_stats:
            daily_stats[date_key] = {"date": date_key, "orders": 0, "revenue": 0.0}

        daily_stats[date_key]["orders"] += 1
        daily_stats[date_key]["revenue"] += float(order.total_price)

    return {"period_days": days, "daily_stats": list(daily_stats.values())}


# ------------------------
# Users
# ------------------------

@router.get("/users")
async def get_all_users(
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Get all users"""
    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at,
        }
        for user in users
    ]
