from fastapi import APIRouter, Depends

from schemas.auth import LoginRequest, RegisterRequest
from services.auth_helpers import get_current_user
from services.auth_service import login, logout, register


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login_api(payload: LoginRequest) -> dict:
    return login(payload)


@router.post("/register")
def register_api(payload: RegisterRequest) -> dict:
    return register(payload)


@router.post("/logout")
def logout_api(current_user: dict = Depends(get_current_user)) -> dict:
    return logout(current_user)
