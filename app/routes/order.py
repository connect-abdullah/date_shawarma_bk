from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.entities.order.service import OrderService
from app.entities.order.schema import OrderCreate, OrderRead, OrderUpdate, OrderReadWithItems
from app.core.response import APIResponse, ok, fail
from app.core.auth import get_current_admin_id, get_current_customer_id

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=APIResponse[OrderRead])
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    customer_id: int = Depends(get_current_customer_id),
):
    try:
        data = payload.model_dump()
        data["customer_id"] = customer_id
        order = OrderService(db).create(OrderCreate(**data))
        return ok(data=order, message="Order created")
    except Exception as e:
        return fail(message=str(e))


@router.get("/me", response_model=APIResponse[list[OrderRead]])
def my_orders(
    db: Session = Depends(get_db),
    customer_id: int = Depends(get_current_customer_id),
):
    try:
        orders = OrderService(db).get_by_customer(customer_id)
        return ok(data=orders, message="Orders retrieved")
    except Exception as e:
        return fail(message=str(e))


@router.get("", response_model=APIResponse[list[OrderRead]])
def list_orders(db: Session = Depends(get_db), _: int = Depends(get_current_admin_id)):
    try:
        orders = OrderService(db).get_all()
        return ok(data=orders, message="Orders retrieved")
    except Exception as e:
        return fail(message=str(e))


@router.get("/admin/{order_id}", response_model=APIResponse[OrderReadWithItems])
def get_order_admin(
    order_id: int,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_admin_id),
):
    """Admin: get any order by ID with items."""
    try:
        order = OrderService(db).get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return ok(data=order, message="Order retrieved")
    except HTTPException:
        raise
    except Exception as e:
        return fail(message=str(e))


@router.get("/{order_id}", response_model=APIResponse[OrderReadWithItems])
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    customer_id: int = Depends(get_current_customer_id),
):
    """Customer: get own order by ID with items."""
    try:
        order = OrderService(db).get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.customer_id != customer_id:
            raise HTTPException(status_code=403, detail="Not allowed to view this order")
        return ok(data=order, message="Order retrieved")
    except HTTPException:
        raise
    except Exception as e:
        return fail(message=str(e))


@router.put("/{order_id}", response_model=APIResponse[OrderRead])
def update_order(
    order_id: int,
    payload: OrderUpdate,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_admin_id),
):
    try:
        order = OrderService(db).update(order_id, payload)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return ok(data=order, message="Order updated")
    except HTTPException:
        raise
    except Exception as e:
        return fail(message=str(e))
