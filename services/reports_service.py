from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from database import get_db
from services.mongo_helpers import BadObjectIdError, day_range_utc, to_object_id

def get_shop_summary(shop_id: str | None, period: str) -> dict:
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing shop_id for current user")
        
    db = get_db()
    
    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    now = datetime.now(tz=timezone.utc)
    start_time = None
    
    if period == "today":
        start_time, _ = day_range_utc(now.date())
    elif period == "week":
        # Start of current week (Monday)
        days_since_monday = now.weekday()
        start_date = (now - timedelta(days=days_since_monday)).date()
        start_time, _ = day_range_utc(start_date)
    elif period == "month":
        start_date = now.replace(day=1).date()
        start_time, _ = day_range_utc(start_date)

    query = {
        "shop_id": shop_obj_id,
        "status": "closed"
    }
    if start_time:
        query["closed_at"] = {"$gte": start_time}
        
    closed_sessions = list(db.table_sessions.find(query))
    total_closed_sessions = len(closed_sessions)
    total_revenue = sum(session.get("total_paid", 0.0) for session in closed_sessions)
    
    # Calculate total orders linked to these exact closed sessions
    session_ids = [session["_id"] for session in closed_sessions]
    total_orders = 0
    top_items: list[dict] = []
    if session_ids:
        # We only count orders that were successfully paid (ignoring cancelled ones inside the session)
        total_orders = db.orders.count_documents({
            "session_id": {"$in": session_ids},
            "status": "paid"
        })

        pipeline = [
            {"$match": {"session_id": {"$in": session_ids}, "status": "paid"}},
            {"$unwind": "$items"},
            {
                "$group": {
                    "_id": "$items.product_id",
                    "name": {"$first": "$items.name"},
                    "quantity": {"$sum": "$items.quantity"},
                    "revenue": {
                        "$sum": {
                            "$multiply": ["$items.unit_price", "$items.quantity"]
                        }
                    },
                }
            },
            {"$sort": {"quantity": -1, "revenue": -1}},
            {"$limit": 5},
        ]
        top_items = list(db.orders.aggregate(pipeline))
        for item in top_items:
            item["product_id"] = str(item.pop("_id"))
        
    average_bill = total_revenue / total_closed_sessions if total_closed_sessions > 0 else 0.0

    return {
        "period": period,
        "total_revenue": total_revenue,
        "total_closed_sessions": total_closed_sessions,
        "total_orders": total_orders,
        "average_bill_per_session": average_bill,
        "top_items": top_items,
        "currency": "USD" # Can be dynamic later
    }
