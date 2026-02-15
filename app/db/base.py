from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class BaseModel:
    """Base model with common fields for all tables."""

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
