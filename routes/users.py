from fastapi import APIRouter

from schemas.users import AssignShopRequest
from services.users_service import assign_shop_to_user


router = APIRouter(tags=["users"])


@router.post("/users/assign-shop")
def assign_shop_to_user_api(payload: AssignShopRequest) -> dict:
    return assign_shop_to_user(payload.user_id, payload.shop_id)
