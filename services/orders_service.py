from datetime import datetime, timezone

from fastapi import HTTPException
from pymongo import ReturnDocument

from database import get_db
from schemas.orders import OrderCreateRequest
from services.mongo_helpers import BadObjectIdError, serialize_document, to_object_id


VALID_ORDER_STATUSES = {"pending", "preparing", "served", "cancelled"}


def create_order(payload: OrderCreateRequest, shop_id: str | None) -> dict:
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing shop_id for current user")
        
    db = get_db()

    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
        table_obj_id = to_object_id(payload.table_id, "table_id")
        session_obj_id = to_object_id(payload.session_id, "session_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    session = db.table_sessions.find_one({"_id": session_obj_id, "shop_id": shop_obj_id, "status": "open"})
    if not session:
        raise HTTPException(status_code=404, detail="Open session not found")

    items = [item.model_dump() for item in payload.items]
    total_amount = sum(item["quantity"] * item["unit_price"] for item in items)

    order_doc = {
        "shop_id": shop_obj_id,
        "table_id": table_obj_id,
        "session_id": session_obj_id,
        "items": items,
        "notes": payload.notes,
        "status": payload.status,
        "total_amount": total_amount,
        "created_at": datetime.now(tz=timezone.utc),
    }

    inserted = db.orders.insert_one(order_doc)
    created = db.orders.find_one({"_id": inserted.inserted_id})
    return serialize_document(created)


def get_orders(shop_id: str | None, session_id: str | None, status: str | None) -> list[dict]:
    if not shop_id:
        return []
        
    db = get_db()
    query: dict = {}

    try:
        if shop_id:
            query["shop_id"] = to_object_id(shop_id, "shop_id")
        if session_id:
            query["session_id"] = to_object_id(session_id, "session_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if status:
        query["status"] = status

    orders = db.orders.find(query).sort("created_at", -1)
    return [serialize_document(order) for order in orders]


def update_order_status(order_id: str, status: str, shop_id: str | None) -> dict:
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing shop_id for current user")
        
    db = get_db()

    if status not in VALID_ORDER_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid order status")

    try:
        order_obj_id = to_object_id(order_id, "id")
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    updated = db.orders.find_one_and_update(
        {"_id": order_obj_id, "shop_id": shop_obj_id},
        {"$set": {"status": status}},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")

    return serialize_document(updated)
