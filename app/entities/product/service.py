from sqlalchemy.orm import Session
from app.entities.product.model import Product
from app.entities.product.schema import ProductCreate, ProductRead, ProductUpdate


class ProductService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: ProductCreate) -> ProductRead:
        product = Product(**payload.model_dump())
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return ProductRead.model_validate(product)

    def get_by_id(self, product_id: int) -> ProductRead | None:
        p = self.db.query(Product).filter(Product.id == product_id).first()
        return ProductRead.model_validate(p) if p else None

    def get_all(self, featured_only: bool = False, trending_only: bool = False) -> list[ProductRead]:
        q = self.db.query(Product).filter(Product.is_active == True, Product.is_available == True)
        if featured_only:
            q = q.filter(Product.is_featured == True)
        if trending_only:
            q = q.filter(Product.is_trending == True)
        return [ProductRead.model_validate(p) for p in q.all()]

    def update(self, product_id: int, payload: ProductUpdate) -> ProductRead | None:
        p = self.db.query(Product).filter(Product.id == product_id).first()
        if not p:
            return None
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(p, key, value)
        self.db.commit()
        self.db.refresh(p)
        return ProductRead.model_validate(p)

    def delete(self, product_id: int) -> bool:
        p = self.db.query(Product).filter(Product.id == product_id).first()
        if not p:
            return False
        p.is_active = False
        self.db.commit()
        return True
