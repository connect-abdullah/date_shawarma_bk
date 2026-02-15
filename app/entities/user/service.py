from sqlalchemy.orm import Session
from app.entities.user.model import User, UserRoleEnum
from app.entities.user.schema import (
    UserCreate,
    UserRead,
    UserCreateResponse,
    UserUpdate,
    UserLogin,
    UserTokenResponse,
    ForgotPassword,
)
from app.core.security import get_password_hash, verify_password, create_token
from app.core.email import EmailService
from app.core.logging import get_logger
from fastapi import HTTPException
from datetime import datetime, timezone

logger = get_logger(__name__)


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.email_service = EmailService()

    def check_email_exists(self, email: str) -> bool:
        return self.db.query(User).filter(User.email == email).first() is not None

    def create_user(self, payload: UserCreate) -> UserCreateResponse:
        if self.check_email_exists(payload.email):
            raise ValueError("User with this email already exists")
        data = payload.model_dump()
        data["password"] = get_password_hash(data["password"])
        user = User(**data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        role_val = user.user_role.value
        token = create_token({"sub": str(user.id), "role": role_val})
        return UserCreateResponse(
            user=UserRead.model_validate(user),
            access_token=token,
            token_type="Bearer",
        )

    def get_by_id(self, user_id: int) -> UserRead | None:
        user = self.db.query(User).filter(User.id == user_id).first()
        return UserRead.model_validate(user) if user else None

    def update_user(self, user_id: int, payload: UserUpdate) -> UserRead | None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        data = payload.model_dump(exclude_unset=True)
        if data.get("password"):
            data["password"] = get_password_hash(data["password"])
        for key, value in data.items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return UserRead.model_validate(user)

    def delete_user(self, user_id: int) -> bool:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True

    def login_user(self, payload: UserLogin) -> UserTokenResponse:
        user = self.db.query(User).filter(User.email == payload.email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        if not verify_password(payload.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid password")
        role_val = user.user_role.value
        token = create_token({"sub": str(user.id), "role": role_val})
        return UserTokenResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            user_role=user.user_role,
            access_token=token,
            token_type="Bearer",
        )

    def reset_password(self, payload: ForgotPassword) -> bool:
        user = self.db.query(User).filter(User.email == payload.email).first()
        if not user:
            return False
        from app.core.security import generate_random_password
        new_password = generate_random_password(15)
        user.password = get_password_hash(new_password)
        self.db.commit()
        self.email_service.send_email(
            payload.email,
            "Password Reset - Date Shawarma",
            f"Your new password is: {new_password}",
        )
        return True
