from fastapi import APIRouter, Query

from schemas.table_sessions import TableSessionCreateRequest
from services.table_sessions_service import create_table_session, get_open_table_sessions


router = APIRouter(tags=["table_sessions"])


@router.post("/table-sessions")
def create_table_session_api(payload: TableSessionCreateRequest) -> dict:
    return create_table_session(payload)


@router.get("/table-sessions/open")
def get_open_table_sessions_api(
    shop_id: str | None = Query(default=None),
    table_id: str | None = Query(default=None),
) -> list[dict]:
    return get_open_table_sessions(shop_id, table_id)
