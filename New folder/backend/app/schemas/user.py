from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=3, max_length=100)
    role: Optional[str] = Field(default="customer", pattern="^(customer|waiter|kitchen|admin)$")

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class User(UserBase):
    id: int
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User