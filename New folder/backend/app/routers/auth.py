from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.cart import Cart
from ..schemas.user import UserCreate, UserLogin, Token, User as UserSchema
from ..dependencies.auth import create_access_token, get_current_user
import hashlib

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

def md5_hash(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
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

    new_user = User(
        name=user_data.name,
        email=user_data.email.lower(),
        password=md5_hash(user_data.password),  # 🔐 MD5 hash
        role=user_data.role or "customer"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    if new_user.role == "customer":
        new_cart = Cart(user_id=new_user.id)
        db.add(new_cart)
        db.commit()

    access_token = create_access_token(data={"sub": str(new_user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserSchema.from_orm(new_user)
    }


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email.lower()).first()

    if not user or user.password != md5_hash(credentials.password):  # 🔐 MD5 check
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserSchema.from_orm(user)
    }
