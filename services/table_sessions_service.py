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

    table = db.tables.find_one({"_id": table_obj_id, "shop_id": shop_obj_id})
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    existing_open = db.table_sessions.find_one(
        {"table_id": table_obj_id, "shop_id": shop_obj_id, "status": "open"}
    )
    if existing_open:
        raise HTTPException(status_code=409, detail="Table already has an open session")

    guest_count = int(table.get("capacity", 0))

    session_doc = {
        "table_id": table_obj_id,
        "shop_id": shop_obj_id,
        "opened_by": user_id,
        "status": "open",
        "opened_at": datetime.now(tz=timezone.utc),
        "closed_at": None,
        "guest_count": guest_count,
    }

    inserted = db.table_sessions.insert_one(session_doc)
    db.tables.find_one_and_update(
        {"_id": table_obj_id, "shop_id": shop_obj_id},
        {"$set": {"status": "occupied"}},
    )
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


def update_table_session_guest_count(session_id: str, guest_count: int, shop_id: str | None) -> dict:
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing shop_id for current user")

    db = get_db()

    try:
        session_obj_id = to_object_id(session_id, "session_id")
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    session = db.table_sessions.find_one({"_id": session_obj_id, "shop_id": shop_obj_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.get("status") != "open":
        raise HTTPException(status_code=400, detail="Session is not open")

    updated = db.table_sessions.find_one_and_update(
        {"_id": session_obj_id, "shop_id": shop_obj_id},
        {"$set": {"guest_count": guest_count}},
        return_document=ReturnDocument.AFTER,
    )
    return serialize_document(updated)



