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
        return ReviewRead(
            id=review.id,
            product_name=review.product.name,
            user_name=review.user.name,
            rating=review.rating,
            comment=review.comment,
            is_approved=review.is_approved
        )

    def get_by_id(self, review_id: int) -> ReviewRead | None:
        r = self.db.query(Review).filter(Review.id == review_id).first()
        return ReviewRead.model_validate(r) if r else None

    def get_by_product(self, product_id: int) -> list[ReviewRead]:
        reviews = self.db.query(Review).filter(Review.product_id == product_id, Review.is_approved == True).all()
        if not reviews:
            return []
        reviews_data = []
        for review in reviews:
            reviews_data.append(ReviewRead(
                id=review.id,
                product_name=review.product.name,
                user_name=review.user.name,
                rating=review.rating,
                comment=review.comment,
                is_approved=review.is_approved
            ))
        return reviews_data
    
    def get_all(self) -> list[ReviewRead]:
        reviews = self.db.query(Review).all()
        reviews_data = []
        for review in reviews:
            reviews_data.append(ReviewRead(
                id=review.id,
                product_name=review.product.name,
                user_name=review.user.name,
                rating=review.rating,
                comment=review.comment,
                is_approved=review.is_approved
            ))
        return reviews_data

    def update(self, review_id: int, payload: ReviewUpdate) -> ReviewRead | None:
        review = self.db.query(Review).filter(Review.id == review_id).first()
        if not review:
            return None
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(review, key, value)
        self.db.commit()
        self.db.refresh(review)
        return ReviewRead(
            id=review.id,
            product_name=review.product.name,
            user_name=review.user.name,
            rating=review.rating,
            comment=review.comment,
            is_approved=review.is_approved
        )

    def approve(self, review_id: int) -> ReviewRead | None:
        return self.update(review_id, ReviewUpdate(is_approved=True))
    
    def delete(self, review_id:int) -> bool:
        review = self.db.query(Review).filter(Review.id == review_id).first()
        if not review:
            return False
        self.db.delete(review)
        self.db.commit()
        return True

