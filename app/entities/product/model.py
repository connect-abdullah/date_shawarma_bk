from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base, BaseModel


class Product(Base, BaseModel):
    __tablename__ = "products"

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    short_description = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    photo = Column(String, nullable=True)
    is_featured = Column(Boolean, default=False, nullable=True)
    is_trending = Column(Boolean, nullable=True, default=False)
    is_available = Column(Boolean, default=True, nullable=False)

    variants = relationship(
        "ProductVariant",
        backref="product",
        cascade="all, delete-orphan",
    )
    order_items = relationship(
        "OrderItem",
        backref="product",
        passive_deletes=True,
    )
    reviews = relationship(
        "Review",
        backref="product",
        cascade="all, delete-orphan",
    )
