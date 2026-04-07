from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from typing import List
from datetime import datetime, timedelta

from ..database import get_db
from ..models.user import User
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
    db = Depends(get_db),
):
    """Create new menu item including image_url"""
    new_item = item_data.model_dump()
    new_item["created_at"] = datetime.utcnow()
    new_item["updated_at"] = datetime.utcnow()
    if "available" not in new_item or new_item["available"] is None:
        new_item["available"] = True
        
    result = await db.menu_items.insert_one(new_item)
    new_item["id"] = str(result.inserted_id)
    return new_item


@router.put("/menu/{item_id}", response_model=MenuItemSchema)
async def update_menu_item(
    item_id: str,
    item_data: MenuItemUpdate,
    current_user: User = Depends(require_role(["admin"])),
    db = Depends(get_db),
):
    """Update menu item including image_url"""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid item ID")
    
    obj_id = ObjectId(item_id)
    item = await db.menu_items.find_one({"_id": obj_id})
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")

    update_data = item_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    await db.menu_items.update_one({"_id": obj_id}, {"$set": update_data})
    
    updated_item = await db.menu_items.find_one({"_id": obj_id})
    updated_item["id"] = str(updated_item["_id"])
    return updated_item


@router.delete("/menu/{item_id}")
async def delete_menu_item(
    item_id: str,
    current_user: User = Depends(require_role(["admin"])),
    db = Depends(get_db),
):
    """Delete menu item"""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid item ID")
        
    obj_id = ObjectId(item_id)
    result = await db.menu_items.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")

    return {"message": "Menu item deleted successfully"}


@router.put("/menu/{item_id}/toggle")
async def toggle_menu_item_availability(
    item_id: str,
    current_user: User = Depends(require_role(["admin"])),
    db = Depends(get_db),
):
    """Toggle availability"""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid item ID")
    
    obj_id = ObjectId(item_id)
    item = await db.menu_items.find_one({"_id": obj_id})
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")

    new_status = not item.get("available", True)
    await db.menu_items.update_one({"_id": obj_id}, {"$set": {"available": new_status, "updated_at": datetime.utcnow()}})
    
    updated_item = await db.menu_items.find_one({"_id": obj_id})
    updated_item["id"] = str(updated_item["_id"])
    return updated_item


# ------------------------
# Analytics
# ------------------------

@router.get("/analytics/overview")
async def get_analytics_overview(
    current_user: User = Depends(require_role(["admin"])),
    db = Depends(get_db),
):
    """Dashboard analytics"""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Today's orders
    today_orders = await db.orders.find({"created_at": {"$gte": today}}).to_list(None)
    today_revenue = sum(order.get("total_price", 0) for order in today_orders)

    # Active orders
    active_orders = await db.orders.count_documents({"status": {"$ne": "Served"}})

    # Week's orders
    week_orders = await db.orders.find({"created_at": {"$gte": week_ago}}).to_list(None)
    week_revenue = sum(order.get("total_price", 0) for order in week_orders)

    # Month's orders
    month_orders = await db.orders.find({"created_at": {"$gte": month_ago}}).to_list(None)
    month_revenue = sum(order.get("total_price", 0) for order in month_orders)

    # Status breakdown
    status_breakdown = {}
    valid_statuses = ["Placed", "Preparing", "Cooking", "Ready to Serve", "Served", "Cancelled"]
    for s in valid_statuses:
        status_breakdown[s] = await db.orders.count_documents({"status": s})

    # Popular items
    pipeline = [
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$items.item_id",
            "name": {"$first": "$items.name"},
            "total_quantity": {"$sum": "$items.quantity"}
        }},
        {"$sort": {"total_quantity": -1}},
        {"$limit": 10}
    ]
    popular_items_cursor = db.orders.aggregate(pipeline)
    popular_items = []
    async for item in popular_items_cursor:
        popular_items.append({
            "name": item.get("name", "Unknown"),
            "quantity": item.get("total_quantity", 0)
        })

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
        "popular_items": popular_items,
    }


@router.get("/analytics/orders")
async def get_orders_analytics(
    days: int = 7,
    current_user: User = Depends(require_role(["admin"])),
    db = Depends(get_db),
):
    """Analytics for last N days"""
    start_date = datetime.utcnow() - timedelta(days=days)

    orders = await db.orders.find({"created_at": {"$gte": start_date}}).sort("created_at", -1).to_list(None)

    daily_stats = {}

    for order in orders:
        if "created_at" in order:
            date_key = order["created_at"].date().isoformat()
            if date_key not in daily_stats:
                daily_stats[date_key] = {"date": date_key, "orders": 0, "revenue": 0.0}

            daily_stats[date_key]["orders"] += 1
            daily_stats[date_key]["revenue"] += float(order.get("total_price", 0))

    return {"period_days": days, "daily_stats": list(daily_stats.values())}


# ------------------------
# Users
# ------------------------

@router.get("/users")
async def get_all_users(
    current_user: User = Depends(require_role(["admin"])),
    db = Depends(get_db),
):
    """Get all users"""
    users = await db.users.find({}).to_list(None)

    return [
        {
            "id": str(user["_id"]),
            "name": user.get("name"),
            "email": user.get("email"),
            "role": user.get("role"),
            "created_at": user.get("created_at"),
        }
        for user in users
    ]
