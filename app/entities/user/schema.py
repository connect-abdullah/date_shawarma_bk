from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.entities.user.model import UserRoleEnum


class UserBase(BaseModel):
    name: str
    email: str
    phone: str | None = None
    address: str | None = None
    user_role: UserRoleEnum


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


class UserCreateResponse(BaseModel):
    user: UserRead
    access_token: str
    token_type: str = "Bearer"


class UserTokenResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    user_role: UserRoleEnum
    access_token: str
    token_type: str


class ForgotPassword(BaseModel):
    email: str
