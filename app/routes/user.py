from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.entities.user.service import UserService
from app.entities.user.schema import (
    UserCreate,
    UserRead,
    UserUpdate,
    UserLogin,
    UserTokenResponse,
    ForgotPassword,
    AdminDashboardResponse,
)
from app.entities.user.model import UserRoleEnum
from app.core.response import APIResponse, ok, fail
from app.core.auth import get_current_admin_id, get_current_user_id
from app.cache import generate_cache_key, get_cache, set_cache

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=APIResponse[UserTokenResponse])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        result = UserService(db).create_user(user)
        return ok(data=result, message="User created successfully")
    except ValueError as e:
        return fail(message=str(e))


@router.get("/me", response_model=APIResponse[UserRead])
def get_me(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    try:
        user = UserService(db).get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return ok(data=user, message="Profile retrieved")
    except HTTPException:
        raise
    except Exception as e:
        return fail(message=str(e))
    
@router.get("/admin-dashboard", response_model=APIResponse[AdminDashboardResponse])
def admin_dashboard(db: Session = Depends(get_db), admin_id: int = Depends(get_current_admin_id)):
    try:
         # Generate cache key
        cache_key = generate_cache_key("admin-dashboard")
        # Check cache
        dashboard = get_cache(cache_key)
        if dashboard is not None:
            return ok(data=dashboard, message="Admin dashboard retrieved from cache")
        if not admin_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        dashboard = UserService(db).admin_dashboard()
        # Cache the result
        set_cache(cache_key, dashboard, ttl=900) # 15 minutes
        return ok(data=dashboard, message="Admin dashboard retrieved")
    except HTTPException:
        raise
    except Exception as e:
        return fail(message=str(e))


@router.get("/{user_id}", response_model=APIResponse[UserRead])
def get_user(user_id: int, db: Session = Depends(get_db), _: int = Depends(get_current_admin_id)):
    try:
        user = UserService(db).get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return ok(data=user, message="User retrieved")
    except HTTPException:
        raise
    except Exception as e:
        return fail(message=str(e))


@router.put("/update-me", response_model=APIResponse[UserRead])
def update_user(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        updated = UserService(db).update_user(user_id, payload)
        if not updated:
            raise HTTPException(status_code=404, detail="User not found")
        return ok(data=updated, message="User updated")
    except HTTPException:
        raise
    except Exception as e:
        return fail(message=str(e))


@router.delete("/{user_id}", response_model=APIResponse[bool])
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: int = Depends(get_current_admin_id),
):
    try:
        deleted = UserService(db).delete_user(user_id)
        return ok(data=deleted, message="User deleted")
    except Exception as e:
        return fail(message=str(e))


@router.post("/login", response_model=APIResponse[UserTokenResponse])
def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        token = UserService(db).login_user(user)
        return ok(data=token, message="Login successful")
    except HTTPException:
        raise
    except Exception as e:
        return fail(message=str(e))


@router.post("/forgot-password", response_model=APIResponse[bool])
def forgot_password(payload: ForgotPassword, db: Session = Depends(get_db)):
    """Forgot password: send a new password to the user's email if the account exists."""
    try:
        result = UserService(db).reset_password(payload)
        return ok(data=result, message="Password successfully sent to email")
    except HTTPException:
        raise
    except Exception as e:
        return fail(message=str(e))
