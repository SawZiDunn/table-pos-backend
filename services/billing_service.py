from datetime import datetime, timezone

from fastapi import HTTPException

from database import get_db
from services.mongo_helpers import BadObjectIdError, serialize_document, to_object_id


def get_table_session_bill(session_id: str, shop_id: str | None) -> dict:
    """Calculate total bill for a table session from all orders."""
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

    orders = db.orders.find({"session_id": session_obj_id})
    total_bill = sum(order.get("total_amount", 0) for order in orders)
    order_count = db.orders.count_documents({"session_id": session_obj_id})

    return {
        "session_id": session_id,
        "table_id": str(session.get("table_id", "")),
        "shop_id": str(session.get("shop_id", "")),
        "total_bill": total_bill,
        "order_count": order_count,
        "status": session.get("status"),
    }


def close_table_session(session_id: str, shop_id: str | None) -> dict:
    """Close a table session and free the table for next customer."""
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

    # Check if all orders are paid
    unpaid_orders = db.orders.find_one(
        {"session_id": session_obj_id, "status": {"$ne": "paid"}}
    )
    if unpaid_orders:
        raise HTTPException(status_code=400, detail="Cannot close session with unpaid orders")

    # Close session
    db.table_sessions.find_one_and_update(
        {"_id": session_obj_id},
        {
            "$set": {
                "status": "closed",
                "closed_at": datetime.now(tz=timezone.utc),
            }
        },
    )

    # Free the table
    table_id = session.get("table_id")
    if table_id:
        db.tables.find_one_and_update(
            {"_id": table_id},
            {"$set": {"status": "available"}},
        )

    updated_session = db.table_sessions.find_one({"_id": session_obj_id})
    return serialize_document(updated_session)
