from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum

from pydantic import BaseModel, EmailStr

from .models import UserRole

# ------------------ User Schemas ------------------
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    user_id: int
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:

        from_attributes = True


class AdminUserCreate(UserBase):
    password: str
    role: UserRole 


# ------------------ Product Schemas ------------------

class ProductBase(BaseModel):
    name: str
    description: str
    brand: Optional[str] = None
    price: float
    discount_price: Optional[float] = None
    is_active: Optional[bool] = True

    category_name: str
    subcategory_name: Optional[str] = None

    class Config:
        from_attributes = True


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):

    product_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# New class for updating product details (only by admin)
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    discount_price: Optional[float] = None
    is_active: Optional[bool] = None
    category_name: Optional[str] = None
    subcategory_name: Optional[str] = None


# ------------------ Address Schemas ------------------

class AddressBase(BaseModel):
    user_id: int
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    country: str = "India"
    postal_code: str
    is_default_shipping: Optional[bool] = False
    is_default_billing: Optional[bool] = False

    class Config:
        from_attributes = True


class AddressCreate(AddressBase):
    pass


class Address(AddressBase):
    address_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schema for a user creating their OWN address
class AddressCreateByUser(BaseModel):
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    country: str = "India"
    postal_code: str
    is_default_shipping: Optional[bool] = False
    is_default_billing: Optional[bool] = False


# ------------------ OrderDetail Schemas ------------------

class OrderDetailBase(BaseModel):
    product_id: int
    quantity: int


class OrderDetailCreate(OrderDetailBase):
    pass


class OrderDetail(OrderDetailBase):
    order_detail_id: int
    order_id: int  # Links back to the parent order table
    price_at_purchase: float
    created_at: datetime

    class Config:
        from_attributes = True


# ------------------ Order Schemas ------------------

class OrderCreate(BaseModel):
    user_id: int
    shipping_address_id: int
    billing_address_id: int

    # The list of items being purchased
    items: List[OrderDetailCreate]  # Uses the list of line items defined above


class OrderStatusSchema(str, PyEnum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class OrderCreateByUser(BaseModel): 
    shipping_address_id: int
    billing_address_id: int
    items: List[OrderDetailCreate]

class Order(BaseModel):
    order_id: int
    user_id: int
    shipping_address_id: int
    billing_address_id: int
    order_date: datetime
    total_amount: float
    status: OrderStatusSchema

    # Include the list of line items in the response

    details: List[OrderDetail]

    class Config:
        from_attributes = True