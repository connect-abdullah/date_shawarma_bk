from sqlalchemy.orm import Session, joinedload, selectinload
from app.entities.product.model import Product
from app.entities.product.schema import ProductCreate, ProductRead, ProductUpdate, ProductListHomePage
from app.entities.product_variant.model import ProductVariant
from app.entities.product_variant.schema import ProductVariantRead
from app.entities.review.model import Review
from app.entities.review.schema import ReviewRead
from app.entities.order_item.model import OrderItem
from app.entities.order.model import Order


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
        product = (
            self.db.query(Product)
            .options(
                joinedload(Product.variants),
                joinedload(Product.reviews).joinedload(Review.user),
            )
            .filter(Product.id == product_id)
            .first()
        )
        if not product:
            return None
        return ProductRead(
            id=product.id,
            name=product.name,
            description=product.description,
            short_description=product.short_description,
            category_id=product.category_id,
            photo=product.photo,
            is_featured=bool(product.is_featured),
            is_available=bool(product.is_available),
            variants=[ProductVariantRead.model_validate(v) for v in product.variants],
            reviews=[
                ReviewRead(
                    id=review.id,
                    product_name=product.name,
                    user_name=review.user.name,
                    rating=review.rating,
                    comment=review.comment,
                    is_approved=review.is_approved,
                )
                for review in product.reviews
            ],
        )

    def get_all(
        self,
        featured_only: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ProductListHomePage]:
        q = self.db.query(Product).options(
            joinedload(Product.category),
            selectinload(Product.variants),
            selectinload(Product.reviews),
        )
        if featured_only:
            q = q.filter(Product.is_featured == True)  # noqa: E712
        q = q.order_by(Product.id).offset(offset).limit(limit)

        products = q.all()
        results: list[ProductListHomePage] = []

        for p in products:
            # Home page needs a "default" variant (first variant).
            # If a product has no variants yet, add one first.
            if not getattr(p, "variants", None):
                continue
            v0 = p.variants[0]
            approved_ratings = [r.rating for r in getattr(p, "reviews", []) if getattr(r, "is_approved", False)]
            review_count = len(approved_ratings)
            avg_rating = (sum(approved_ratings) / review_count) if review_count else None
            category = getattr(p, "category", None)
            category_name = getattr(category, "category_name", "") or "" if category else ""

            results.append(
                ProductListHomePage(
                    id=p.id,
                    name=p.name,
                    photo=p.photo or "",
                    short_description=p.short_description or "",
                    category_id=p.category_id,
                    category_name=category_name,
                    is_featured=bool(p.is_featured),
                    variant_name=v0.variant_name,
                    s_variant_price=float(v0.price),
                    variant_product_id=v0.product_id,
                    variant_id=v0.id,
                    is_available=bool(p.is_available),
                    review_count=review_count,
                    avg_rating=avg_rating,
                )
            )

        return results

    def update(self, product_id: int, payload: ProductUpdate) -> ProductRead | None:
        p = self.db.query(Product).filter(Product.id == product_id).first()
        if not p:
            return None
        # Update only plain product fields; exclude "variants" so we never assign payload list to p.variants (ORM relationship)
        product_data = payload.model_dump(exclude_unset=True, exclude={"variants"})
        for key, value in product_data.items():
            setattr(p, key, value)
        # Handle variants from payload (plain dicts / Pydantic only; no ORM instances)
        if payload.variants is not None:
            for v in payload.variants:
                v_dict = v.model_dump(exclude_unset=True)
                vid = v_dict.pop("id", None)
                if vid:
                    variant = self.db.query(ProductVariant).filter(ProductVariant.id == vid).first()
                    if variant:
                        for k, val in v_dict.items():
                            setattr(variant, k, val)
                else:
                    self.db.add(
                        ProductVariant(
                            product_id=product_id,
                            variant_name=v.variant_name or "",
                            price=v.price or 0,
                        )
                    )
        self.db.commit()
        self.db.refresh(p)
        # Build ProductRead the same way as get_by_id (reviews need product_name/user_name from relations)
        return self.get_by_id(product_id)

    def delete(self, product_id: int) -> bool:
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return False
        # Delete orders that contain this product (cascade deletes their order_items)
        order_ids = [
            row[0]
            for row in self.db.query(OrderItem.order_id)
            .filter(OrderItem.product_id == product_id)
            .distinct()
            .all()
        ]
        for oid in order_ids:
            order = self.db.query(Order).filter(Order.id == oid).first()
            if order:
                self.db.delete(order)
        self.db.delete(product)
        self.db.commit()
        return True
