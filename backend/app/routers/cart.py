from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from ..database import get_db
from ..models.user import User
from ..schemas.cart import CartItemCreate, CartItemUpdate, CartResponse
from ..dependencies.auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/api/cart", tags=["Cart"])

@router.get("/", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's cart"""
    user_id_str = str(current_user.id)
    cart = await db.carts.find_one({"user_id": user_id_str})
    
    if not cart:
        # Create cart if doesn't exist
        cart = {
            "user_id": user_id_str,
            "items": [],
            "updated_at": datetime.utcnow()
        }
        result = await db.carts.insert_one(cart)
        cart["_id"] = result.inserted_id
    
    cart_items = []
    total = 0.0
    
    items_list = cart.get("items", [])
    
    for item in items_list:
        menu_item_id = item.get("menu_item_id")
        if not ObjectId.is_valid(menu_item_id):
            continue
            
        m_obj_id = ObjectId(menu_item_id)
        menu_item = await db.menu_items.find_one({"_id": m_obj_id})
            
        if menu_item:
            cart_items.append({
                "item_id": menu_item_id,
                "quantity": item.get("quantity", 1),
                "price": menu_item.get("price", 0.0),
                "item_name": menu_item.get("name", "Unknown"),
                "item_description": menu_item.get("description", "")
            })
            total += menu_item.get("price", 0.0) * item.get("quantity", 1)
    
    return {
        "id": str(cart["_id"]),
        "user_id": user_id_str,
        "items": cart_items,
        "total": total
    }

@router.post("/items", status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    cart_item: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Add item to cart"""
    if not ObjectId.is_valid(cart_item.item_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid menu item ID"
        )
        
    obj_id = ObjectId(cart_item.item_id)
    menu_item = await db.menu_items.find_one({"_id": obj_id})
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    
    if not menu_item.get("available", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Menu item is not available"
        )
    
    user_id_str = str(current_user.id)
    cart = await db.carts.find_one({"user_id": user_id_str})
    if not cart:
        cart = {
            "user_id": user_id_str,
            "items": [],
            "updated_at": datetime.utcnow()
        }
        await db.carts.insert_one(cart)
    
    # Check if item already in cart
    items = cart.get("items", [])
    existing_item = next((i for i in items if i["menu_item_id"] == cart_item.item_id), None)
    
    if existing_item:
        # Update quantity
        await db.carts.update_one(
            {"user_id": user_id_str, "items.menu_item_id": cart_item.item_id},
            {"$inc": {"items.$.quantity": cart_item.quantity}, "$set": {"updated_at": datetime.utcnow()}}
        )
        return {"message": "Cart item quantity updated"}
    else:
        # Add new item
        new_item = {
            "menu_item_id": cart_item.item_id,
            "name": menu_item.get("name"),
            "price": menu_item.get("price"),
            "quantity": cart_item.quantity,
            "image_url": menu_item.get("image_url")
        }
        await db.carts.update_one(
            {"user_id": user_id_str},
            {"$push": {"items": new_item}, "$set": {"updated_at": datetime.utcnow()}}
        )
        return {"message": "Item added to cart"}

@router.put("/items/{item_id}")
async def update_cart_item(
    item_id: str,
    update_data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update cart item quantity"""
    user_id_str = str(current_user.id)
    cart = await db.carts.find_one({"user_id": user_id_str})
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
        
    items = cart.get("items", [])
    existing_item = next((i for i in items if i["menu_item_id"] == item_id), None)
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not in cart"
        )
    
    if update_data.quantity <= 0:
        # Remove item
        await db.carts.update_one(
            {"user_id": user_id_str},
            {"$pull": {"items": {"menu_item_id": item_id}}, "$set": {"updated_at": datetime.utcnow()}}
        )
        return {"message": "Item removed from cart"}
    
    await db.carts.update_one(
        {"user_id": user_id_str, "items.menu_item_id": item_id},
        {"$set": {"items.$.quantity": update_data.quantity, "updated_at": datetime.utcnow()}}
    )
    return {"message": "Cart item updated"}

@router.delete("/items/{item_id}")
async def remove_from_cart(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Remove item from cart"""
    user_id_str = str(current_user.id)
    cart = await db.carts.find_one({"user_id": user_id_str})
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
        
    await db.carts.update_one(
        {"user_id": user_id_str},
        {"$pull": {"items": {"menu_item_id": item_id}}, "$set": {"updated_at": datetime.utcnow()}}
    )
    return {"message": "Item removed from cart"}

@router.delete("/clear")
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Clear all items from cart"""
    user_id_str = str(current_user.id)
    await db.carts.update_one(
        {"user_id": user_id_str},
        {"$set": {"items": [], "updated_at": datetime.utcnow()}}
    )
    return {"message": "Cart cleared"}