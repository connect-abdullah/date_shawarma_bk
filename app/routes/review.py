from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.entities.review.service import ReviewService
from app.entities.review.schema import ReviewCreate, ReviewRead, ReviewUpdate
from app.core.response import APIResponse, ok, fail
from app.core.auth import get_current_user_id, get_current_admin_id

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", response_model=APIResponse[ReviewRead])
def create_review(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        data = payload.model_dump()
        data["user_id"] = user_id
        review = ReviewService(db).create(ReviewCreate(**data))
        return ok(data=review, message="Review submitted")
    except Exception as e:
        return fail(message=str(e))


@router.get("/product/{product_id}", response_model=APIResponse[list[ReviewRead]])
def get_reviews_by_product(
    product_id: int,
    db: Session = Depends(get_db),
    approved_only: bool = True,
):
    try:
        reviews = ReviewService(db).get_by_product(product_id, approved_only=approved_only)
        return ok(data=reviews, message="Reviews retrieved")
    except Exception as e:
        return fail(message=str(e))


@router.put("/{review_id}/approve", response_model=APIResponse[ReviewRead])
def approve_review(
    review_id: int,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_admin_id),
):
    try:
        review = ReviewService(db).approve(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        return ok(data=review, message="Review approved")
    except HTTPException:
        raise
    except Exception as e:
        return fail(message=str(e))


@router.put("/{review_id}", response_model=APIResponse[ReviewRead])
def update_review(
    review_id: int,
    payload: ReviewUpdate,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_admin_id),
):
    try:
        review = ReviewService(db).update(review_id, payload)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        return ok(data=review, message="Review updated")
    except HTTPException:
        raise
    except Exception as e:
        return fail(message=str(e))
