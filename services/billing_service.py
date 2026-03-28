from datetime import datetime, timezone

from fastapi import HTTPException

from database import get_db
from services.mongo_helpers import BadObjectIdError, serialize_document, to_object_id


def _calculate_bill(subtotal: float, tax_percent: float) -> tuple[float, float, float]:
    rounded_subtotal = round(float(subtotal), 2)
    safe_tax_percent = max(0.0, min(float(tax_percent or 0), 100.0))
    tax_amount = round((rounded_subtotal * safe_tax_percent) / 100.0, 2)
    total_bill = round(rounded_subtotal + tax_amount, 2)
    return rounded_subtotal, tax_amount, total_bill


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

    shop = db.shops.find_one({"_id": shop_obj_id})
    shop_settings = (shop or {}).get("settings", {})
    tax_percent = shop_settings.get("tax_percent", 0)

    orders = db.orders.find({"session_id": session_obj_id, "status": {"$ne": "cancelled"}})
    subtotal = sum(order.get("total_amount", 0) for order in orders)
    order_count = db.orders.count_documents({"session_id": session_obj_id, "status": {"$ne": "cancelled"}})
    subtotal, tax_amount, total_bill = _calculate_bill(subtotal, tax_percent)

    return {
        "session_id": session_id,
        "table_id": str(session.get("table_id", "")),
        "shop_id": str(session.get("shop_id", "")),
        "subtotal": subtotal,
        "tax_percent": tax_percent,
        "tax_amount": tax_amount,
        "total_bill": total_bill,
        "order_count": order_count,
        "status": session.get("status"),
    }


def checkout_table_session(session_id: str, payment_method: str, shop_id: str | None) -> dict:
    """Pay for all orders in a session, close the session, and free the table atomically."""
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

    # Mark all orders as paid
    db.orders.update_many(
        {"session_id": session_obj_id, "status": {"$ne": "cancelled"}},
        {"$set": {"status": "paid"}}
    )
    
    # Calculate final total
    shop = db.shops.find_one({"_id": shop_obj_id})
    shop_settings = (shop or {}).get("settings", {})
    tax_percent = shop_settings.get("tax_percent", 0)

    paid_orders = db.orders.find({"session_id": session_obj_id, "status": "paid"})
    subtotal = sum(order.get("total_amount", 0) for order in paid_orders)
    subtotal, tax_amount, total_amount = _calculate_bill(subtotal, tax_percent)

    # Close session and save payment metadata
    db.table_sessions.find_one_and_update(
        {"_id": session_obj_id},
        {
            "$set": {
                "status": "closed",
                "closed_at": datetime.now(tz=timezone.utc),
                "payment_method": payment_method,
                "subtotal": subtotal,
                "tax_percent": tax_percent,
                "tax_amount": tax_amount,
                "total_paid": total_amount,
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
