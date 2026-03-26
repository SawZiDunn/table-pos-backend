from fastapi import APIRouter

from schemas.auth import LoginRequest, RegisterRequest
from services.auth_service import login, register


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login_api(payload: LoginRequest) -> dict:
    return login(payload)


@router.post("/register")
def register_api(payload: RegisterRequest) -> dict:
    return register(payload)
