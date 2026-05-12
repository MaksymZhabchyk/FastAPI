"""Pydantic схеми для Order та OrderItem."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    order_id: int
    total_price: float
    
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    user_id: int
    status: str = "pending"
    notes: Optional[str] = None


class OrderCreate(BaseModel):
    user_id: int
    notes: Optional[str] = None
    items: Optional[List[OrderItemCreate]] = None


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class Order(OrderBase):
    id: int
    total_amount: float
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class OrderInDB(Order):
    pass