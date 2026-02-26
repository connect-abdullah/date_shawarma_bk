from pydantic import BaseModel
from datetime import datetime


class ComplaintBoxBase(BaseModel):
    user_name: str
    user_email: str
    phone: str | None = None
    comment: str


class ComplaintBoxCreate(ComplaintBoxBase):
    pass


class ComplaintBoxRead(ComplaintBoxBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
