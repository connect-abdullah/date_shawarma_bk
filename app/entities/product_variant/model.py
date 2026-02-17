from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base, BaseModel


class ProductVariant(Base, BaseModel):
    __tablename__ = "product_variants"

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_name = Column(String, nullable=False)  # e.g., "Small", "Medium", "Large", "XL"
    price = Column(Numeric(10, 2), nullable=False)

    order_items = relationship("OrderItem", backref="variant")

