from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.entities.order.model import Order, OrderStatusEnum
from app.entities.order_item.model import OrderItem
from app.entities.order.schema import OrderCreate, OrderRead, OrderUpdate, OrderReadWithItems, OrderItemRead


class OrderService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: OrderCreate) -> OrderRead:
        order_date = payload.order_date or datetime.now(timezone.utc)
        order = Order(
            customer_id=payload.customer_id,
            order_status=payload.order_status,
            order_date=order_date,
            total_price=payload.total_price,
        )
        self.db.add(order)
        self.db.flush()
        for item in payload.items:
            oi = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            self.db.add(oi)
        self.db.commit()
        self.db.refresh(order)
        return OrderRead.model_validate(order)

    def get_by_id(self, order_id: int) -> OrderReadWithItems | None:
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return None
        data = OrderRead.model_validate(order).model_dump()
        data["order_items"] = [OrderItemRead.model_validate(oi) for oi in order.order_items]
        return OrderReadWithItems(**data)

    def get_by_customer(self, customer_id: int) -> list[OrderRead]:
        orders = self.db.query(Order).filter(Order.customer_id == customer_id).all()
        return [OrderRead.model_validate(o) for o in orders]

    def get_all(self) -> list[OrderRead]:
        orders = self.db.query(Order).all()
        return [OrderRead.model_validate(o) for o in orders]

    def update(self, order_id: int, payload: OrderUpdate) -> OrderRead | None:
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return None
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(order, key, value)
        self.db.commit()
        self.db.refresh(order)
        return OrderRead.model_validate(order)
