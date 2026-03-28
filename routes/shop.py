from fastapi import APIRouter, Depends

from schemas.shop import ShopCreateRequest, ShopUpsertRequest
from services.auth_helpers import get_current_user
from services.shop_service import create_shop, get_shop, upsert_shop


router = APIRouter(tags=["shop"])


@router.get("/shop")
def get_shop_api(current_user: dict = Depends(get_current_user)) -> dict | None:
    return get_shop(current_user.get("shop_id"))


@router.put("/shop")
def upsert_shop_api(payload: ShopUpsertRequest, current_user: dict = Depends(get_current_user)) -> dict:
    return upsert_shop(payload)


@router.post("/shop")
def create_shop_api(payload: ShopCreateRequest) -> dict:
    return create_shop(payload)
