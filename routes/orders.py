from fastapi import APIRouter, Depends, Query

from schemas.orders import OrderCreateRequest, OrderStatusUpdateRequest
from services.auth_helpers import get_current_user
from services.orders_service import create_order, get_orders, update_order_status


router = APIRouter(tags=["orders"])


@router.post("/orders")
def create_order_api(payload: OrderCreateRequest, current_user: dict = Depends(get_current_user)) -> dict:
    return create_order(payload, current_user.get("shop_id"))


@router.get("/orders")
def get_orders_api(
    session_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    current_user: dict = Depends(get_current_user)
) -> list[dict]:
    return get_orders(current_user.get("shop_id"), session_id, status)


@router.put("/orders/{id}/status")
def update_order_status_api(id: str, payload: OrderStatusUpdateRequest, current_user: dict = Depends(get_current_user)) -> dict:
    return update_order_status(id, payload.status, current_user.get("shop_id"))
