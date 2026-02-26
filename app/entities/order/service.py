from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.entities.order.model import Order, OrderStatusEnum
from app.entities.order_item.model import OrderItem
from app.entities.order.schema import OrderCreate, OrderRead, OrderUpdate, OrderReadWithItems, ListItems


class OrderService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: OrderCreate, user_id: int) -> OrderRead:
        order = Order(
            customer_id=user_id,
            order_status=OrderStatusEnum.PENDING,
            order_date=datetime.now(timezone.utc),
            total_price=payload.total_price,
            payment_method=payload.payment_method,
        )
        self.db.add(order)
        self.db.flush()
        for item in payload.items:
            oi = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                variant_id=item.variant_id,
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
        list_items = []
        for oi in order.order_items:
            list_items.append(ListItems(
                id=oi.id,
                product_id=oi.product_id,
                product_name=oi.product.name,
                variant_id=oi.variant_id,
                variant_name=oi.variant.variant_name,
                quantity=oi.quantity,
                unit_price=oi.unit_price,
                order_id=oi.order_id,
                total_price=order.total_price,
                payment_method=order.payment_method,
                customer_name=order.customer.name,
                customer_address=order.customer.address,
                created_at=order.created_at,
            ))
        data["order_items"] = list_items
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
    
    def delete(self, order_id: int) -> bool:
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return False
        self.db.delete(order)
        self.db.commit()
        return True