from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# User Models
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


# Product Models
class ProductResponse(BaseModel):
    id: int
    product_id: Optional[int]
    product_name: str
    description: Optional[str]
    price: float
    stock_quantity: int
    category: Optional[str]
    availability_status: Optional[str]
    created_date: Optional[datetime]


# Order Models
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    total_amount: float


class OrderItemResponse(BaseModel):
    order_item_id: Optional[str]
    product_id: int
    product_name: Optional[str]
    quantity: int
    unit_price: float
    stock_quantity: Optional[int]


class OrderResponse(BaseModel):
    id: int
    order_id: str
    order_date: datetime
    total_amount: float
    order_status: str
    items: List[OrderItemResponse]


# SQL Query Model
class SQLQuery(BaseModel):
    query: str

