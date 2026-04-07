from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..database import get_db
from ..models.menu import MenuItem
from ..models.user import User
from ..schemas.menu import MenuItem as MenuItemSchema, MenuItemCreate, MenuItemUpdate
from ..dependencies.auth import get_current_user, require_role

from bson import ObjectId

router = APIRouter(prefix="/api/menu", tags=["Menu"])

@router.get("/", response_model=List[MenuItemSchema])
async def get_menu(
    category: str = None,
    available: bool = None,
    db = Depends(get_db)
):
    """Get all menu items with optional filters"""
    query = {}
    if category:
        query["category"] = category
    if available is not None:
        query["available"] = available
    
    cursor = db.menu_items.find(query)
    items = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        items.append(doc)
    return items

@router.get("/{item_id}", response_model=MenuItemSchema)
async def get_menu_item(item_id: str, db = Depends(get_db)):
    """Get specific menu item"""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid menu item ID"
        )
    
    obj_id = ObjectId(item_id)
    item = await db.menu_items.find_one({"_id": obj_id})
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    item["id"] = str(item["_id"])
    return item

@router.get("/categories/list")
async def get_categories(db = Depends(get_db)):
    """Get all unique categories"""
    categories = await db.menu_items.distinct("category")
    return {"categories": categories}