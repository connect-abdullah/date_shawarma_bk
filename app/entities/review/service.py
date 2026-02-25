from sqlalchemy.orm import Session
from app.entities.review.model import Review
from app.entities.review.schema import ReviewCreate, ReviewRead, ReviewUpdate


class ReviewService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: ReviewCreate, user_id: int) -> ReviewRead:
        
        review = Review(
            product_id=payload.product_id,
            user_id=user_id,
            rating=payload.rating,
            comment=payload.comment,
            is_approved=False,
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return ReviewRead.model_validate(review)

    def get_by_id(self, review_id: int) -> ReviewRead | None:
        r = self.db.query(Review).filter(Review.id == review_id).first()
        return ReviewRead.model_validate(r) if r else None

    def get_by_product(self, product_id: int, approved_only: bool = True) -> list[ReviewRead]:
        q = self.db.query(Review).filter(Review.product_id == product_id)
        if approved_only:
            q = q.filter(Review.is_approved == True)
        return [ReviewRead.model_validate(r) for r in q.all()]

    def update(self, review_id: int, payload: ReviewUpdate) -> ReviewRead | None:
        r = self.db.query(Review).filter(Review.id == review_id).first()
        if not r:
            return None
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(r, key, value)
        self.db.commit()
        self.db.refresh(r)
        return ReviewRead.model_validate(r)

    def approve(self, review_id: int) -> ReviewRead | None:
        return self.update(review_id, ReviewUpdate(is_approved=True))
    
    def delete(self, review_id:int) -> bool:
        v = self.db.query(Review).filter(Review.id == review_id).first()
        if not v:
            return False
        v.is_active = False # add delete command for variant, not is_active
        self.db.commit()
        return True

