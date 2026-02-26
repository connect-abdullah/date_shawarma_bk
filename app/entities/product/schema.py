from decimal import Decimal
from pydantic import BaseModel
from app.entities.product_variant.schema import ProductVariantRead
from app.entities.review.schema import ReviewRead
from app.entities.product_variant.schema import ProductVariantCreate, ProductVariantUpdate


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    short_description: str | None = None
    category_id: int
    photo: str | None = None
    is_featured: bool = False
    is_available: bool = True


class ProductCreate(ProductBase):
    variants: list[ProductVariantCreate] = []
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    short_description: str | None = None
    category_id: int | None = None
    variants: list[ProductVariantUpdate] | None = None
    photo: str | None = None
    is_featured: bool | None = None
    is_available: bool | None = None


class ProductRead(ProductBase):
    id: int
    variants: list[ProductVariantRead] = []  # size/options 
    reviews: list[ReviewRead] = []

    class Config:
        from_attributes = True

class ProductListHomePage(BaseModel):
    id: int
    name: str
    photo: str
    short_description: str
    category_id: int
    cateogry_name: str
    is_featured: bool
    variant_name: str
    s_variant_price: float
    variant_product_id: int
    variant_id: int
    is_available: bool

    class Config:
        from_attributes = True