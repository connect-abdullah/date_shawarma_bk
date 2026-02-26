from sqlalchemy.orm import Session
from app.entities.product_variant.model import ProductVariant
from app.entities.product_variant.schema import (
    ProductVariantCreate,
    ProductVariantRead,
    ProductVariantUpdate,
)


class ProductVariantService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: ProductVariantCreate) -> ProductVariantRead:
        variant = ProductVariant(**payload.model_dump())
        self.db.add(variant)
        self.db.commit()
        self.db.refresh(variant)
        return ProductVariantRead.model_validate(variant)

    def get_by_id(self, variant_id: int) -> ProductVariantRead | None:
        v = self.db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
        return ProductVariantRead.model_validate(v) if v else None

    def get_by_product(self, product_id: int) -> list[ProductVariantRead]:
        variants = (
            self.db.query(ProductVariant)
            .filter(ProductVariant.product_id == product_id, ProductVariant.is_active == True)
            .all()
        )
        return [ProductVariantRead.model_validate(v) for v in variants]

    def update(self, variant_id: int, payload: ProductVariantUpdate) -> ProductVariantRead | None:
        v = self.db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
        if not v:
            return None
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(v, key, value)
        self.db.commit()
        self.db.refresh(v)
        return ProductVariantRead.model_validate(v)

    def delete(self, variant_id: int) -> bool:
        variant = self.db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
        if not variant:
            return False
        self.db.delete(variant)
        self.db.commit()
        return True

