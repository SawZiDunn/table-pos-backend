from fastapi import APIRouter, Query

from schemas.shop import ShopCreateRequest, ShopUpsertRequest
from services.shop_service import create_shop, get_shops, upsert_shop


router = APIRouter(tags=["shop"])


@router.get("/shop")
def get_shop_api(user_id: str = Query(...)) -> list[dict]:
    return get_shops(user_id)


@router.put("/shop")
def upsert_shop_api(payload: ShopUpsertRequest) -> dict:
    return upsert_shop(payload)


@router.post("/shop")
def create_shop_api(payload: ShopCreateRequest) -> dict:
    return create_shop(payload)
