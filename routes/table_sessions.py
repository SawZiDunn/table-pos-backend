from fastapi import APIRouter, Depends, Query

from schemas.table_sessions import (
    TableSessionCreateRequest,
    TableSessionCheckoutRequest,
    TableSessionGuestCountUpdateRequest,
)
from services.auth_helpers import get_current_user
from services.table_sessions_service import (
    create_table_session,
    get_open_table_sessions,
    update_table_session_guest_count,
)
from services.billing_service import get_table_session_bill, checkout_table_session


router = APIRouter(tags=["table_sessions"])


@router.post("/table-sessions")
def create_table_session_api(payload: TableSessionCreateRequest, current_user: dict = Depends(get_current_user)) -> dict:
    return create_table_session(payload, current_user.get("shop_id"), current_user.get("id"))


@router.get("/table-sessions/open")
def get_open_table_sessions_api(
    table_id: str | None = Query(default=None),
    current_user: dict = Depends(get_current_user)
) -> list[dict]:
    return get_open_table_sessions(current_user.get("shop_id"), table_id)


@router.get("/table-sessions/{id}/bill")
def get_table_session_bill_api(id: str, current_user: dict = Depends(get_current_user)) -> dict:
    return get_table_session_bill(id, current_user.get("shop_id"))


@router.post("/table-sessions/{id}/checkout")
def checkout_table_session_api(id: str, payload: TableSessionCheckoutRequest, current_user: dict = Depends(get_current_user)) -> dict:
    return checkout_table_session(id, payload.payment_method, current_user.get("shop_id"))


@router.patch("/table-sessions/{id}/guest-count")
def update_table_session_guest_count_api(
    id: str,
    payload: TableSessionGuestCountUpdateRequest,
    current_user: dict = Depends(get_current_user),
) -> dict:
    return update_table_session_guest_count(id, payload.guest_count, current_user.get("shop_id"))
