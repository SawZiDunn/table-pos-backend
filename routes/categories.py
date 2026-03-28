from fastapi import APIRouter, Depends

from schemas.categories import CategoryCreateRequest
from services.auth_helpers import get_current_user
from services.categories_service import create_category, get_categories


router = APIRouter(tags=["categories"])


@router.get("/categories")
def get_categories_api(current_user: dict = Depends(get_current_user)) -> list[dict]:
    return get_categories(current_user.get("shop_id"))


@router.post("/categories")
def create_category_api(payload: CategoryCreateRequest, current_user: dict = Depends(get_current_user)) -> dict:
    return create_category(payload, current_user.get("shop_id"))
