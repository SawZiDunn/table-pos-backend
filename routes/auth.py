from fastapi import APIRouter

from schemas.auth import LoginRequest
from services.auth_service import login


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login_api(payload: LoginRequest) -> dict:
    return login(payload)
