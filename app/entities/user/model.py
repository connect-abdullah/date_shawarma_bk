from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SQLAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base, BaseModel


class UserRoleEnum(str, Enum):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"


class User(Base, BaseModel):
    __tablename__ = "users"

    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    user_role = Column(SQLAEnum(UserRoleEnum), nullable=False)

    orders = relationship("Order", backref="customer", foreign_keys="Order.customer_id")
    reviews = relationship("Review", backref="user")
