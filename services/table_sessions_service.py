from datetime import datetime, timezone

from fastapi import HTTPException
from pymongo import ReturnDocument

from database import get_db
from schemas.table_sessions import TableSessionCreateRequest
from services.mongo_helpers import BadObjectIdError, serialize_document, to_object_id


def create_table_session(payload: TableSessionCreateRequest, shop_id: str | None, user_id: str | None) -> dict:
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing shop_id for current user")
        
    db = get_db()

    try:
        table_obj_id = to_object_id(payload.table_id, "table_id")
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    existing_open = db.table_sessions.find_one({"table_id": table_obj_id, "status": "open"})
    if existing_open:
        raise HTTPException(status_code=409, detail="Table already has an open session")

    session_doc = {
        "table_id": table_obj_id,
        "shop_id": shop_obj_id,
        "opened_by": user_id,
        "status": "open",
        "opened_at": datetime.now(tz=timezone.utc),
        "closed_at": None,
    }

    inserted = db.table_sessions.insert_one(session_doc)
    created = db.table_sessions.find_one({"_id": inserted.inserted_id})
    return serialize_document(created)


def get_open_table_sessions(shop_id: str | None, table_id: str | None) -> list[dict]:
    if not shop_id:
        return []
        
    db = get_db()

    query: dict = {"status": "open"}
    try:
        if shop_id:
            query["shop_id"] = to_object_id(shop_id, "shop_id")
        if table_id:
            query["table_id"] = to_object_id(table_id, "table_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    sessions = db.table_sessions.find(query)
    return [serialize_document(session) for session in sessions]



