from fastapi import APIRouter, Depends, Query

from schemas.tables import TableCreateRequest, TableUpdateRequest
from services.auth_helpers import require_role
from services.tables_service import create_table, delete_table, get_tables, update_table


router = APIRouter(tags=["tables"])


@router.get("/tables")
def get_tables_api(current_user: dict = Depends(require_role("manager", "staff"))) -> list[dict]:
    return get_tables(current_user.get("shop_id"))


@router.post("/tables")
def create_table_api(
    payload: TableCreateRequest,
    current_user: dict = Depends(require_role("manager")),
) -> dict:
    return create_table(payload, current_user.get("shop_id"))


@router.put("/tables/{id}")
def update_table_api(
    id: str,
    payload: TableUpdateRequest,
    current_user: dict = Depends(require_role("manager", "staff")),
) -> dict:
    return update_table(id, payload, current_user.get("shop_id"))


@router.delete("/tables/{id}")
def delete_table_api(
    id: str,
    current_user: dict = Depends(require_role("manager")),
) -> dict:
    return delete_table(id, current_user.get("shop_id"))
