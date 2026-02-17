from decimal import Decimal
from pydantic import BaseModel
from app.entities.product_variant.schema import ProductVariantRead


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    short_description: str | None = None
    category_id: int
    photo: str | None = None
    is_featured: bool = False
    is_trending: bool = False
    is_available: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    short_description: str | None = None
    category_id: int | None = None
    price: Decimal | None = None
    photo: str | None = None
    is_featured: bool | None = None
    is_trending: bool | None = None
    is_available: bool | None = None


class ProductRead(ProductBase):
    id: int
    variants: list[ProductVariantRead] = []  # size/options from menu.json

    class Config:
        from_attributes = True
