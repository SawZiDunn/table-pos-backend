from fastapi import HTTPException
from pymongo import ReturnDocument

from database import get_db
from schemas.tables import TableCreateRequest, TableUpdateRequest
from services.mongo_helpers import BadObjectIdError, serialize_document, to_object_id


def get_tables(shop_id: str | None) -> list[dict]:
    if not shop_id:
        return []

    db = get_db()
    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    tables = list(db.tables.find({"shop_id": shop_obj_id}))
    open_sessions = db.table_sessions.find(
        {"shop_id": shop_obj_id, "status": "open"},
        {"table_id": 1},
    )
    open_table_ids = {str(session.get("table_id")) for session in open_sessions}

    result = []
    for table in tables:
        table_id_str = str(table.get("_id"))
        serialized = serialize_document(table)
        serialized["status"] = "occupied" if table_id_str in open_table_ids else "available"
        result.append(serialized)

    return result


def create_table(payload: TableCreateRequest, shop_id: str | None) -> dict:
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing shop_id for current user")

    db = get_db()

    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    existing_table = db.tables.find_one({"shop_id": shop_obj_id, "table_number": payload.table_number})
    if existing_table:
        raise HTTPException(status_code=409, detail="Table number already exists")

    table_doc = {
        "shop_id": shop_obj_id,
        "table_number": payload.table_number,
        "capacity": payload.capacity,
        "status": payload.status,
        "is_active": True,
    }

    inserted = db.tables.insert_one(table_doc)
    created = db.tables.find_one({"_id": inserted.inserted_id})
    return serialize_document(created)


def update_table(table_id: str, payload: TableUpdateRequest, shop_id: str | None) -> dict:
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing shop_id for current user")

    db = get_db()

    try:
        table_obj_id = to_object_id(table_id, "id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    existing_table = db.tables.find_one({"_id": table_obj_id})
    if not existing_table:
        raise HTTPException(status_code=404, detail="Table not found")

    if existing_table.get("shop_id") != shop_obj_id:
        raise HTTPException(status_code=403, detail="Shop access denied")

    updates = payload.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated = db.tables.find_one_and_update(
        {"_id": table_obj_id},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    return serialize_document(updated)


def delete_table(table_id: str, shop_id: str | None) -> dict:
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing shop_id for current user")

    db = get_db()

    try:
        table_obj_id = to_object_id(table_id, "id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    existing_table = db.tables.find_one({"_id": table_obj_id})
    if not existing_table:
        raise HTTPException(status_code=404, detail="Table not found")

    if existing_table.get("shop_id") != shop_obj_id:
        raise HTTPException(status_code=403, detail="Shop access denied")

    open_session = db.table_sessions.find_one(
        {"table_id": table_obj_id, "shop_id": shop_obj_id, "status": "open"}
    )
    if open_session:
        raise HTTPException(status_code=400, detail="Cannot delete table with an open session")

    orders_result = db.orders.delete_many({"table_id": table_obj_id, "shop_id": shop_obj_id})
    sessions_result = db.table_sessions.delete_many({"table_id": table_obj_id, "shop_id": shop_obj_id})
    table_result = db.tables.delete_one({"_id": table_obj_id, "shop_id": shop_obj_id})
    if table_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Table not found")

    return {
        "deleted_table_id": table_id,
        "deleted_sessions": sessions_result.deleted_count,
        "deleted_orders": orders_result.deleted_count,
    }
