from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum as SQLAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base, BaseModel


class OrderStatusEnum(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    READY = "READY"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class Order(Base, BaseModel):
    __tablename__ = "orders"

    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_status = Column(SQLAEnum(OrderStatusEnum), nullable=False)
    order_date = Column(DateTime(timezone=True), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)

    order_items = relationship("OrderItem", backref="order", cascade="all, delete-orphan")
