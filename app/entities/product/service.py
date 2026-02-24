from sqlalchemy.orm import Session
from app.entities.product.model import Product
from app.entities.product.schema import ProductCreate, ProductRead, ProductUpdate, ProductListHomePage
from app.entities.product_variant.model import ProductVariant


class ProductService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: ProductCreate) -> ProductRead:
        product = Product(**payload.model_dump(exclude={"variants"}))
        self.db.add(product)
        self.db.flush()  # get product.id from DB before creating variants
        for v in payload.variants:
            variant = ProductVariant(
                product_id=product.id,
                variant_name=v.variant_name,
                price=v.price,
            )
            self.db.add(variant)
        self.db.commit()
        self.db.refresh(product) 
        return ProductRead.model_validate(product)

    def get_by_id(self, product_id: int) -> ProductRead | None:
        p = self.db.query(Product).filter(Product.id == product_id).first()
        return ProductRead.model_validate(p) if p else None

    def get_all(
        self,
        featured_only: bool = False,
        limit: int = 20,
    ) -> list[ProductListHomePage]:
        q = self.db.query(Product)
        
        if featured_only:
            q = q.filter(Product.is_featured == True)  # noqa: E712

        # Hard limit page size
        q = q.order_by(Product.id).limit(limit)

        products = q.all()
        results: list[ProductListHomePage] = []

        for p in products:
            # Home page needs a "default" variant (first variant).
            # If a product has no variants yet, skip it (or add one first).
            if not getattr(p, "variants", None):
                continue
            v0 = p.variants[0]

            results.append(
                ProductListHomePage(
                    id=p.id,
                    name=p.name,
                    photo=p.photo or "",
                    short_description=p.short_description or "",
                    category_id=p.category_id,
                    cateogry_name=getattr(getattr(p, "category", None), "category_name", "") or "",
                    is_featured=bool(p.is_featured),
                    variant_name=v0.variant_name,
                    s_variant_price=v0.price,
                    variant_product_id=v0.product_id,
                    variant_id=v0.id,
                    is_available=p.is_available,
                )
            )

        return results

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
