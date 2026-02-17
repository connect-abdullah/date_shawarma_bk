from sqlalchemy import Column, Integer, Numeric, ForeignKey
from app.db.base import Base, BaseModel


class OrderItem(Base, BaseModel):
    __tablename__ = "order_items"

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    # Optional: which variant of the product was ordered (size, pieces, etc.)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    quantity = Column(Integer, nullable=False)
    # Snapshot of price at time of order (from variant.price)
    unit_price = Column(Numeric(10, 2), nullable=False)
