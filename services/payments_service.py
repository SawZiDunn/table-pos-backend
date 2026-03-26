from datetime import datetime, timezone

from fastapi import HTTPException
from pymongo import ReturnDocument

from database import get_db
from schemas.payments import PaymentCreateRequest
from services.mongo_helpers import BadObjectIdError, serialize_document, to_object_id


def create_payment(payload: PaymentCreateRequest) -> dict:
    db = get_db()

    try:
        shop_obj_id = to_object_id(payload.shop_id, "shop_id")
        order_obj_id = to_object_id(payload.order_id, "order_id")
        session_obj_id = to_object_id(payload.session_id, "session_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    order = db.orders.find_one({"_id": order_obj_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    payment_doc = {
        "shop_id": shop_obj_id,
        "order_id": order_obj_id,
        "session_id": session_obj_id,
        "amount": payload.amount,
        "method": payload.method,
        "paid_at": datetime.now(tz=timezone.utc),
    }

    inserted = db.payments.insert_one(payment_doc)
    db.orders.find_one_and_update(
        {"_id": order_obj_id},
        {"$set": {"status": "paid"}},
        return_document=ReturnDocument.AFTER,
    )

    created = db.payments.find_one({"_id": inserted.inserted_id})
    return serialize_document(created)
