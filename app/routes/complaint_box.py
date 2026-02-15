from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.entities.complaint_box.service import ComplaintBoxService
from app.entities.complaint_box.schema import ComplaintBoxCreate, ComplaintBoxRead
from app.core.response import APIResponse, ok, fail
from app.core.auth import get_current_admin_id

router = APIRouter(prefix="/complaints", tags=["Complaint Box"])


@router.post("", response_model=APIResponse[ComplaintBoxRead])
def submit_complaint(payload: ComplaintBoxCreate, db: Session = Depends(get_db)):
    try:
        complaint = ComplaintBoxService(db).create(payload)
        return ok(data=complaint, message="Complaint submitted")
    except Exception as e:
        return fail(message=str(e))


@router.get("", response_model=APIResponse[list[ComplaintBoxRead]])
def list_complaints(
    db: Session = Depends(get_db),
    _: int = Depends(get_current_admin_id),
):
    try:
        complaints = ComplaintBoxService(db).get_all()
        return ok(data=complaints, message="Complaints retrieved")
    except Exception as e:
        return fail(message=str(e))
