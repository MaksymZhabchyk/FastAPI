from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.schemas.profile import Profile


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    profile: Optional[Profile] = None

    class Config:
        from_attributes = True


class UserInDB(User):
    hashed_password: str
