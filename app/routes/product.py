from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.entities.product.service import ProductService
from app.entities.product.schema import ProductCreate, ProductRead, ProductUpdate, ProductListHomePage
from app.core.response import APIResponse, ok, fail
from app.core.auth import get_current_admin_id

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=APIResponse[ProductRead])
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_admin_id),
):
    try:
        product = ProductService(db).create(payload)
        return ok(data=product, message="Product created")
    except Exception as e:
        return fail(message=str(e))


@router.get("", response_model=APIResponse[list[ProductListHomePage]])
def list_products(
    db: Session = Depends(get_db),
    featured: bool = Query(False),
    category: str | None = Query(
        default=None,
        description="Optional category key (e.g. 'pizzas', 'burgers', 'wings')",
    ),
    limit: int = Query(
        default=90,
        ge=1,
        le=100,
        description="Max number of products to return",
    ),
):
    try:
        products = ProductService(db).get_all(
            featured_only=featured,
            category=category,
            limit=limit,
        )
        return ok(data=products, message="Products retrieved")
    except Exception as e:
        return fail(message=str(e))


@router.get("/{product_id}", response_model=APIResponse[ProductRead])
def get_product(product_id: int, db: Session = Depends(get_db)):
    try:
        product = ProductService(db).get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return ok(data=product, message="Product retrieved")
    except HTTPException:
        raise
    except Exception as e:
        return fail(message=str(e))


@router.put("/{product_id}", response_model=APIResponse[ProductRead])
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_admin_id),
):
    try:
        product = ProductService(db).update(product_id, payload)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return ok(data=product, message="Product updated")
    except HTTPException:
        raise
    except Exception as e:
        return fail(message=str(e))


@router.delete("/{product_id}", response_model=APIResponse[bool])
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_admin_id),
):
    try:
        deleted = ProductService(db).delete(product_id)
        return ok(data=deleted, message="Product deleted")
    except Exception as e:
        return fail(message=str(e))
