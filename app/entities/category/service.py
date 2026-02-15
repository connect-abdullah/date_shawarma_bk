from sqlalchemy.orm import Session
from app.entities.category.model import Category
from app.entities.category.schema import CategoryCreate, CategoryRead, CategoryUpdate


class CategoryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: CategoryCreate) -> CategoryRead:
        category = Category(**payload.model_dump())
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return CategoryRead.model_validate(category)

    def get_by_id(self, category_id: int) -> CategoryRead | None:
        cat = self.db.query(Category).filter(Category.id == category_id).first()
        return CategoryRead.model_validate(cat) if cat else None

    def get_all(self) -> list[CategoryRead]:
        categories = self.db.query(Category).filter(Category.is_active == True).all()
        return [CategoryRead.model_validate(c) for c in categories]

    def update(self, category_id: int, payload: CategoryUpdate) -> CategoryRead | None:
        cat = self.db.query(Category).filter(Category.id == category_id).first()
        if not cat:
            return None
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(cat, key, value)
        self.db.commit()
        self.db.refresh(cat)
        return CategoryRead.model_validate(cat)

    def delete(self, category_id: int) -> bool:
        cat = self.db.query(Category).filter(Category.id == category_id).first()
        if not cat:
            return False
        cat.is_active = False
        self.db.commit()
        return True
