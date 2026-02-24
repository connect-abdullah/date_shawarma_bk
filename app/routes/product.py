from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.entities.product.service import ProductService
from app.entities.product.schema import ProductCreate, ProductRead, ProductUpdate, ProductListHomePage
from app.core.response import APIResponse, ok, fail
from app.core.auth import get_current_admin_id
from app.cache import get_cache, set_cache, generate_cache_key, invalidate_cache

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=APIResponse[ProductRead])
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_admin_id),
):
    try:
        product = ProductService(db).create(payload)
        # Invalidate cache
        invalidate_cache(prefix="products")
        return ok(data=product, message="Product created")
    except Exception as e:
        return fail(message=str(e))


@router.get("", response_model=APIResponse[list[ProductListHomePage]])
def list_products(
    db: Session = Depends(get_db),
    featured: bool = Query(False),
    limit: int = Query(
        default=90,
        ge=1,
        le=100,
        description="Max number of products to return",
    ),
):
    try:    
        # Generate cache key
        cache_key = generate_cache_key("products", featured=featured, limit=limit)
        # Check cache
        products = get_cache(cache_key)
        if products is not None:
            return ok(data=products, message="Products retrieved from cache")
        
        # Get products from database
        products = ProductService(db).get_all(
            featured_only=featured,
            limit=limit,
        )

        # Cache the result
        set_cache(cache_key, products, ttl=3600) # 1 hour
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
        # Invalidate cache
        invalidate_cache(prefix="products")
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
        # Invalidate cache
        invalidate_cache(prefix="products")
        return ok(data=deleted, message="Product deleted")
    except Exception as e:
        return fail(message=str(e))
