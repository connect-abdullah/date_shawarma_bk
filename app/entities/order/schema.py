from datetime import datetime
from pydantic import BaseModel
from app.entities.order.model import OrderStatusEnum


class OrderItemBase(BaseModel):
    product_id: int
    variant_id: int | None = None  # which size/variant from the menu.json
    quantity: int
    unit_price: float


class OrderItemRead(OrderItemBase):
    id: int
    order_id: int

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    customer_id: int
    order_status: OrderStatusEnum
    order_date: datetime
    total_price: float


class OrderCreate(BaseModel):
    customer_id: int
    order_status: OrderStatusEnum = OrderStatusEnum.PENDING
    order_date: datetime | None = None
    total_price: float
    items: list[OrderItemBase]


class OrderUpdate(BaseModel):
    order_status: OrderStatusEnum | None = None


class OrderRead(OrderBase):
    id: int

    class Config:
        from_attributes = True


class OrderReadWithItems(OrderRead):
    order_items: list[OrderItemRead] = []  # noqa: RUF012

    class Config:
        from_attributes = True
