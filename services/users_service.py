from fastapi import HTTPException
from pymongo import ReturnDocument

from database import get_db
from services.mongo_helpers import BadObjectIdError, serialize_document, to_object_id


def assign_shop_to_user(user_id: str, shop_id: str) -> dict:
    db = get_db()

    try:
        user_obj_id = to_object_id(user_id, "user_id")
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    shop = db.shops.find_one({"_id": shop_obj_id})
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    updated = db.users.find_one_and_update(
        {"_id": user_obj_id},
        {"$set": {"shop_id": shop_obj_id}},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")

    return serialize_document(updated)
