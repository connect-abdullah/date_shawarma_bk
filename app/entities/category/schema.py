from pydantic import BaseModel


class CategoryBase(BaseModel):
    category_name: str
    photo: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    category_name: str | None = None
    photo: str | None = None


class CategoryRead(CategoryBase):
    id: int

    class Config:
        from_attributes = True
