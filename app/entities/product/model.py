from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base, BaseModel


class Product(Base, BaseModel):
    __tablename__ = "products"

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    photo = Column(String, nullable=True)
    is_featured = Column(Boolean, default=False, nullable=True)
    is_trending = Column(Boolean, default=False, nullable=True)
    is_available = Column(Boolean, default=True, nullable=False)

    order_items = relationship("OrderItem", backref="product")
    reviews = relationship("Review", backref="product")
