from datetime import date, datetime, timedelta

from fastapi import HTTPException

from database import get_db
from services.mongo_helpers import BadObjectIdError, day_range_utc, to_object_id


def get_daily_sales(shop_id: str, target_date: date | None) -> dict:
    db = get_db()

    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    day = target_date or datetime.utcnow().date()
    start, end = day_range_utc(day)

    pipeline = [
        {
            "$match": {
                "shop_id": shop_obj_id,
                "paid_at": {"$gte": start, "$lte": end},
            }
        },
        {
            "$group": {
                "_id": None,
                "total_sales": {"$sum": "$amount"},
                "total_payments": {"$sum": 1},
            }
        },
    ]

    summary = list(db.payments.aggregate(pipeline))
    result = summary[0] if summary else {"total_sales": 0, "total_payments": 0}

    return {
        "date": day.isoformat(),
        "shop_id": shop_id,
        "total_sales": result.get("total_sales", 0),
        "total_payments": result.get("total_payments", 0),
    }


def get_monthly_sales(shop_id: str, year: int, month: int) -> dict:
    """Get total sales for a specific month."""
    db = get_db()

    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    start = datetime(year, month, 1, tzinfo=datetime.now().astimezone().tzinfo)
    if month == 12:
        end = datetime(year + 1, 1, 1, tzinfo=start.tzinfo) - timedelta(seconds=1)
    else:
        end = datetime(year, month + 1, 1, tzinfo=start.tzinfo) - timedelta(seconds=1)

    pipeline = [
        {
            "$match": {
                "shop_id": shop_obj_id,
                "paid_at": {"$gte": start, "$lte": end},
            }
        },
        {
            "$group": {
                "_id": None,
                "total_sales": {"$sum": "$amount"},
                "total_payments": {"$sum": 1},
            }
        },
    ]

    summary = list(db.payments.aggregate(pipeline))
    result = summary[0] if summary else {"total_sales": 0, "total_payments": 0}

    return {
        "month": f"{year}-{month:02d}",
        "shop_id": shop_id,
        "total_sales": result.get("total_sales", 0),
        "total_payments": result.get("total_payments", 0),
    }


def get_daily_orders_summary(shop_id: str, target_date: date | None) -> dict:
    """Get order count and statuses for a specific day."""
    db = get_db()

    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    day = target_date or datetime.utcnow().date()
    start, end = day_range_utc(day)

    pipeline = [
        {
            "$match": {
                "shop_id": shop_obj_id,
                "created_at": {"$gte": start, "$lte": end},
            }
        },
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1},
            }
        },
    ]

    results = list(db.orders.aggregate(pipeline))
    status_counts = {r["_id"]: r["count"] for r in results}

    return {
        "date": day.isoformat(),
        "shop_id": shop_id,
        "total_orders": sum(status_counts.values()),
        "pending": status_counts.get("pending", 0),
        "preparing": status_counts.get("preparing", 0),
        "served": status_counts.get("served", 0),
        "paid": status_counts.get("paid", 0),
        "cancelled": status_counts.get("cancelled", 0),
    }


def get_session_summary(session_id: str) -> dict:
    """Get detailed summary for a completed table session."""
    db = get_db()

    try:
        session_obj_id = to_object_id(session_id, "session_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    session = db.table_sessions.find_one({"_id": session_obj_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    orders = list(db.orders.find({"session_id": session_obj_id}))
    total_amount = sum(order.get("total_amount", 0) for order in orders)

    payments = list(db.payments.find({"session_id": session_obj_id}))
    total_paid = sum(payment.get("amount", 0) for payment in payments)

    return {
        "session_id": session_id,
        "table_id": str(session.get("table_id", "")),
        "shop_id": str(session.get("shop_id", "")),
        "status": session.get("status"),
        "opened_at": session.get("opened_at").isoformat() if session.get("opened_at") else None,
        "closed_at": session.get("closed_at").isoformat() if session.get("closed_at") else None,
        "total_orders": len(orders),
        "total_bill": total_amount,
        "total_paid": total_paid,
        "payment_methods": [p.get("method") for p in payments],
    }


def get_table_summary(shop_id: str, table_id: str) -> dict:
    """Get usage summary for a specific table in a shop."""
    db = get_db()

    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
        table_obj_id = to_object_id(table_id, "table_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    sessions = list(db.table_sessions.find({"table_id": table_obj_id, "shop_id": shop_obj_id}))
    total_sessions = len(sessions)
    
    closed_sessions = [s for s in sessions if s.get("status") == "closed"]
    total_revenue = 0
    total_orders = 0
    
    for session in closed_sessions:
        payments = list(db.payments.find({"session_id": session["_id"]}))
        total_revenue += sum(p.get("amount", 0) for p in payments)
        orders_count = db.orders.count_documents({"session_id": session["_id"]})
        total_orders += orders_count

    return {
        "table_id": table_id,
        "shop_id": shop_id,
        "total_sessions": total_sessions,
        "completed_sessions": len(closed_sessions),
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "average_bill": total_revenue / len(closed_sessions) if closed_sessions else 0,
    }
