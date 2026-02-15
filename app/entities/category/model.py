from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base, BaseModel


class Category(Base, BaseModel):
    __tablename__ = "categories"

    category_name = Column(String, nullable=False)
    photo = Column(String, nullable=True)

    products = relationship("Product", backref="category")
