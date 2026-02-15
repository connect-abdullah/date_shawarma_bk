from pydantic import BaseModel


class ComplaintBoxBase(BaseModel):
    user_name: str
    user_email: str
    phone: str | None = None
    comment: str


class ComplaintBoxCreate(ComplaintBoxBase):
    pass


class ComplaintBoxRead(ComplaintBoxBase):
    id: int

    class Config:
        from_attributes = True
