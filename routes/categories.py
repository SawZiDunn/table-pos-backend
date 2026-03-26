from fastapi import APIRouter, Query

from schemas.categories import CategoryCreateRequest
from services.categories_service import create_category, get_categories


router = APIRouter(tags=["categories"])


@router.get("/categories")
def get_categories_api(shop_id: str = Query(...)) -> list[dict]:
    return get_categories(shop_id)


@router.post("/categories")
def create_category_api(payload: CategoryCreateRequest) -> dict:
    return create_category(payload)
