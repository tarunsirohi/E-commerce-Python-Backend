from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum as SQLAlchemyEnum,
    Float,
    Boolean,
    ForeignKey
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from .database import Base


class UserRole(enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)

    # Stores user role and given default as user if we dont specify a role.
    role = Column(SQLAlchemyEnum(UserRole), nullable=False, default=UserRole.user)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Product(Base):
    __tablename__ = "product"

    product_id = Column(Integer, primary_key=True, index=True)      # Primary Key
    category_name = Column(String, index=True, nullable=False)
    subcategory_name = Column(String, index=True, nullable=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    brand = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Address(Base):
    __tablename__ = "address"

    address_id = Column(Integer, primary_key=True, index=True)      # Primary Key
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)      # Foreign Key
    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    country = Column(String, nullable=False, default="India")
    postal_code = Column(String, nullable=False)

    # shipping and billing address info which will be later linked with order table.
    is_default_shipping = Column(Boolean, default=False)
    is_default_billing = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="addresses")


class OrderStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class Order(Base):
    __tablename__ = "order"

    order_id = Column(Integer, primary_key=True, index=True)        # Primary Key
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)      # Foreign Key
    shipping_address_id = Column(Integer, ForeignKey('address.address_id'), nullable=False)     # Foreign Key
    billing_address_id = Column(Integer, ForeignKey('address.address_id'), nullable=False)   # Foreign Key
    order_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)     
    total_amount = Column(Float, nullable=False)
    status = Column(SQLAlchemyEnum(OrderStatus), nullable=False, default=OrderStatus.pending)

    # Relationships
    user = relationship("User", backref="orders")
    details = relationship("OrderDetail", back_populates="order", cascade="all, delete-orphan")
    shipping_address = relationship("Address", foreign_keys=[shipping_address_id], backref="shipped_orders")
    billing_address = relationship("Address", foreign_keys=[billing_address_id], backref="billed_orders")


class OrderDetail(Base):
    __tablename__ = "order_detail"

    order_detail_id = Column(Integer, primary_key=True, index=True)     # Primary Key
    order_id = Column(Integer, ForeignKey('order.order_id'), nullable=False, index=True)        # Foreign Key
    product_id = Column(Integer, ForeignKey('product.product_id'), nullable=False)      # Foreign Key
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="details")
    product = relationship("Product")

    created_at = Column(DateTime(timezone=True), server_default=func.now())