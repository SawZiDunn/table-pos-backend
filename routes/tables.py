from fastapi import APIRouter, Query

from schemas.tables import TableCreateRequest, TableUpdateRequest
from services.tables_service import create_table, get_tables, update_table


router = APIRouter(tags=["tables"])


@router.get("/tables")
def get_tables_api(shop_id: str = Query(...)) -> list[dict]:
    return get_tables(shop_id)


@router.post("/tables")
def create_table_api(payload: TableCreateRequest) -> dict:
    return create_table(payload)


@router.put("/tables/{id}")
def update_table_api(id: str, payload: TableUpdateRequest) -> dict:
    return update_table(id, payload)
