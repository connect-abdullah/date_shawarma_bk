from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.entities.category.service import CategoryService
from app.entities.category.schema import CategoryCreate, CategoryRead, CategoryUpdate
from app.core.response import APIResponse, ok, fail
from app.core.auth import get_current_admin_id

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("", response_model=APIResponse[CategoryRead])
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_admin_id),
):
    try:
        category = CategoryService(db).create(payload)
        return ok(data=category, message="Category created")
    except Exception as e:
        return fail(message=str(e))


@router.get("", response_model=APIResponse[list[CategoryRead]])
def list_categories(db: Session = Depends(get_db)):
    try:
        categories = CategoryService(db).get_all()
        return ok(data=categories, message="Categories retrieved")
    except Exception as e:
        return fail(message=str(e))


@router.get("/{category_id}", response_model=APIResponse[CategoryRead])
def get_category(category_id: int, db: Session = Depends(get_db)):
    try:
        category = CategoryService(db).get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return ok(data=category, message="Category retrieved")
    except HTTPException:
        raise
    except Exception as e:
        return fail(message=str(e))


@router.put("/{category_id}", response_model=APIResponse[CategoryRead])
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_admin_id),
):
    try:
        category = CategoryService(db).update(category_id, payload)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return ok(data=category, message="Category updated")
    except HTTPException:
        raise
    except Exception as e:
        return fail(message=str(e))


@router.delete("/{category_id}", response_model=APIResponse[bool])
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_admin_id),
):
    try:
        deleted = CategoryService(db).delete(category_id)
        return ok(data=deleted, message="Category deleted")
    except Exception as e:
        return fail(message=str(e))
