from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class MessageResponse(BaseModel):
    message: str


class UserMe(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class OrderBrief(BaseModel):
    id: int
    total_amount: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileBrief(BaseModel):
    id: int
    bio: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

    class Config:
        from_attributes = True