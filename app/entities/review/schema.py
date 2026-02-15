from pydantic import BaseModel


class ReviewBase(BaseModel):
    product_id: int
    user_id: int
    rating: int
    comment: str | None = None
    is_approved: bool = False


class ReviewCreate(BaseModel):
    product_id: int
    user_id: int
    rating: int
    comment: str | None = None


class ReviewUpdate(BaseModel):
    rating: int | None = None
    comment: str | None = None
    is_approved: bool | None = None


class ReviewRead(ReviewBase):
    id: int

    class Config:
        from_attributes = True
