from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.entities.user.model import UserRoleEnum
from app.entities.order.model import OrderStatusEnum, PaymentMethodEnum


class UserBase(BaseModel):
    name: str
    email: str
    phone: str | None = None
    address: str | None = None
    user_role: UserRoleEnum = UserRoleEnum.CUSTOMER


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None
    phone: str | None = None
    address: str | None = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserTokenResponse(BaseModel):
    user: UserRead
    access_token: str
    token_type: str = "Bearer"


class ForgotPassword(BaseModel):
    email: str

class RecentOrder(BaseModel):
    id: int
    item_names: list[str]
    total_price: float
    payment_method: PaymentMethodEnum
    order_status: OrderStatusEnum

class AdminDashboardResponse(BaseModel):
    total_users: int
    total_products: int
    total_orders: int
    total_reviews: int
    recent_orders: list[RecentOrder]