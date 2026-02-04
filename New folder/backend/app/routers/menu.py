from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.menu import MenuItem
from ..models.user import User
from ..schemas.menu import MenuItem as MenuItemSchema, MenuItemCreate, MenuItemUpdate
from ..dependencies.auth import get_current_user, require_role

router = APIRouter(prefix="/api/menu", tags=["Menu"])

@router.get("/", response_model=List[MenuItemSchema])
async def get_menu(
    category: str = None,
    available: bool = None,
    db: Session = Depends(get_db)
):
    """Get all menu items with optional filters"""
    query = db.query(MenuItem)
    
    if category:
        query = query.filter(MenuItem.category == category)
    if available is not None:
        query = query.filter(MenuItem.available == available)
    
    items = query.all()
    return items

@router.get("/{item_id}", response_model=MenuItemSchema)
async def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    """Get specific menu item"""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    return item

@router.get("/categories/list")
async def get_categories(db: Session = Depends(get_db)):
    """Get all unique categories"""
    categories = db.query(MenuItem.category).distinct().all()
    return {"categories": [cat[0] for cat in categories]}