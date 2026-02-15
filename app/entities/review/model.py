from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from app.db.base import Base, BaseModel


class Review(Base, BaseModel):
    __tablename__ = "reviews"

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)
    is_approved = Column(Boolean, default=False)
