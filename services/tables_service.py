from fastapi import HTTPException
from pymongo import ReturnDocument

from database import get_db
from schemas.tables import TableCreateRequest, TableUpdateRequest
from services.mongo_helpers import BadObjectIdError, serialize_document, to_object_id


def get_tables(shop_id: str) -> list[dict]:
    db = get_db()
    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    tables = db.tables.find({"shop_id": shop_obj_id})
    return [serialize_document(table) for table in tables]


def create_table(payload: TableCreateRequest, current_user: dict) -> dict:
    db = get_db()

    shop_id = current_user.get("shop_id")
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing shop_id for current user")

    if payload.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="Shop access denied")

    try:
        shop_obj_id = to_object_id(payload.shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    existing_count = db.tables.count_documents({"shop_id": shop_obj_id})
    table_name = f"Table {existing_count + 1}"

    table_doc = {
        "shop_id": shop_obj_id,
        "name": table_name,
        "capacity": payload.capacity,
        "status": payload.status,
        "is_active": True,
    }

    inserted = db.tables.insert_one(table_doc)
    created = db.tables.find_one({"_id": inserted.inserted_id})
    return serialize_document(created)


def update_table(table_id: str, payload: TableUpdateRequest, current_user: dict) -> dict:
    db = get_db()

    try:
        table_obj_id = to_object_id(table_id, "id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    shop_id = current_user.get("shop_id")
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing shop_id for current user")

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
