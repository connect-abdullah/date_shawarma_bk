from decimal import Decimal
from pydantic import BaseModel


class ProductVariantBase(BaseModel):
    product_id: int
    variant_name: str
    price: Decimal


class ProductVariantCreate(ProductVariantBase):
    pass


class ProductVariantUpdate(BaseModel):
    variant_name: str | None = None
    price: Decimal | None = None


class ProductVariantRead(ProductVariantBase):
    id: int

    class Config:
        from_attributes = True

