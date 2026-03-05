from pydantic import BaseModel, ConfigDict
from app.entities.product_variant.schema import (
    ProductVariantCreate,
    ProductVariantRead,
    ProductVariantUpdate,
)
from app.entities.review.schema import ReviewRead


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


class ProductUpdate(BaseModel):
    """All fields optional for PATCH-style updates."""

    name: str | None = None
    description: str | None = None
    short_description: str | None = None
    category_id: int | None = None
    photo: str | None = None
    is_featured: bool | None = None
    is_available: bool | None = None
    variants: list[ProductVariantUpdate] | None = None


class ProductRead(ProductBase):
    id: int
    variants: list[ProductVariantRead] = []
    reviews: list[ReviewRead] = []

    model_config = ConfigDict(from_attributes=True)


class ProductListHomePage(BaseModel):
    id: int
    name: str
    photo: str
    short_description: str
    category_id: int
    category_name: str
    is_featured: bool
    variant_name: str
    s_variant_price: float
    variant_product_id: int
    variant_id: int
    is_available: bool
    review_count: int
    avg_rating: float | None = None

    model_config = ConfigDict(from_attributes=True)