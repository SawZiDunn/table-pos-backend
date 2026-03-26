from fastapi import APIRouter, Query

from schemas.orders import OrderCreateRequest, OrderStatusUpdateRequest
from services.orders_service import create_order, get_orders, update_order_status


router = APIRouter(tags=["orders"])


@router.post("/orders")
def create_order_api(payload: OrderCreateRequest) -> dict:
    return create_order(payload)


@router.get("/orders")
def get_orders_api(
    shop_id: str | None = Query(default=None),
    session_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> list[dict]:
    return get_orders(shop_id, session_id, status)


@router.put("/orders/{id}/status")
def update_order_status_api(id: str, payload: OrderStatusUpdateRequest) -> dict:
    return update_order_status(id, payload.status)
