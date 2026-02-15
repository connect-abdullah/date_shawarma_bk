from sqlalchemy import Column, String
from app.db.base import Base, BaseModel


class ComplaintBox(Base, BaseModel):
    __tablename__ = "complaint_boxes"

    user_name = Column(String, nullable=False)
    user_email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    comment = Column(String, nullable=False)
