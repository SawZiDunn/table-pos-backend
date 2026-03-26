from datetime import date, datetime

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
