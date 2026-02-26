from sqlalchemy.orm import Session
from app.entities.complaint_box.model import ComplaintBox
from app.entities.complaint_box.schema import ComplaintBoxCreate, ComplaintBoxRead


class ComplaintBoxService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: ComplaintBoxCreate) -> ComplaintBoxRead:
        complaint = ComplaintBox(**payload.model_dump())
        self.db.add(complaint)
        self.db.commit()
        self.db.refresh(complaint)
        return ComplaintBoxRead.model_validate(complaint)

    def get_by_id(self, complaint_id: int) -> ComplaintBoxRead | None:
        c = self.db.query(ComplaintBox).filter(ComplaintBox.id == complaint_id).first()
        return ComplaintBoxRead.model_validate(c) if c else None

    def get_all(self) -> list[ComplaintBoxRead]:
        complaints = self.db.query(ComplaintBox).all()
        return [ComplaintBoxRead.model_validate(c) for c in complaints]
    
    def delete(self, complaint_id: int) -> bool:
        complaint = self.db.query(ComplaintBox).filter(ComplaintBox.id == complaint_id).first()
        if not complaint:
            return False
        self.db.delete(complaint)
        self.db.commit()
        return True