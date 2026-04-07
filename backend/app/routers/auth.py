from fastapi import APIRouter, Depends, HTTPException, status
from ..database import get_db
from ..models.user import User
from ..models.cart import Cart
from ..schemas.user import UserCreate, UserLogin, Token, User as UserSchema
from ..dependencies.auth import create_access_token, get_password_hash, verify_password
from datetime import datetime

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db = Depends(get_db)):
    # Check if user already exists in MongoDB
    existing_user = await db.users.find_one({"email": user_data.email.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    valid_roles = ["customer", "waiter", "kitchen", "admin"]
    if user_data.role and user_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )

    # Prepare new user document
    new_user_doc = {
        "name": user_data.name,
        "email": user_data.email.lower(),
        "password": get_password_hash(user_data.password),
        "role": user_data.role or "customer",
        "created_at": datetime.utcnow()
    }

    # Insert into MongoDB
    result = await db.users.insert_one(new_user_doc)
    user_id = str(result.inserted_id)
    
    # Create cart for customers
    if new_user_doc["role"] == "customer":
        await db.carts.insert_one({
            "user_id": user_id,
            "items": [],
            "updated_at": datetime.utcnow()
        })

    # Generate token
    access_token = create_access_token(data={"sub": user_id})

    # Prepare user schema for response
    user_schema_data = {
        "id": user_id,
        "name": new_user_doc["name"],
        "email": new_user_doc["email"],
        "role": new_user_doc["role"],
        "created_at": new_user_doc["created_at"]
    }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_schema_data
    }

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db = Depends(get_db)):
    # Find user in MongoDB
    user_doc = await db.users.find_one({"email": credentials.email.lower()})

    if not user_doc or not verify_password(credentials.password, user_doc["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = str(user_doc["_id"])
    access_token = create_access_token(data={"sub": user_id})

    # Prepare user schema for response
    user_schema_data = {
        "id": user_id,
        "name": user_doc.get("name"),
        "email": user_doc.get("email"),
        "role": user_doc.get("role"),
        "created_at": user_doc.get("created_at")
    }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_schema_data
    }
