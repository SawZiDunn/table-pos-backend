from fastapi import HTTPException
from pymongo import ReturnDocument

from database import get_db
from schemas.shop import ShopCreateRequest, ShopUpsertRequest
from services.mongo_helpers import BadObjectIdError, serialize_document, to_object_id


def get_shops(user_id: str) -> list[dict]:
    db = get_db()
    try:
        user_obj_id = to_object_id(user_id, "user_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    shops = db.shops.find({"user_id": user_obj_id})
    return [serialize_document(shop) for shop in shops]


def upsert_shop(payload: ShopUpsertRequest) -> dict:
    db = get_db()

    try:
        user_obj_id = to_object_id(payload.user_id, "user_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    update_doc = {
        "user_id": user_obj_id,
        "name": payload.name,
        "address": payload.address,
        "is_active": payload.is_active,
    }

    if payload.id:
        try:
            shop_obj_id = to_object_id(payload.id, "id")
        except BadObjectIdError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        result = db.shops.find_one_and_update(
            {"_id": shop_obj_id, "user_id": user_obj_id},
            {"$set": update_doc},
            return_document=ReturnDocument.AFTER,
        )
        if not result:
            raise HTTPException(status_code=404, detail="Shop not found")
        return serialize_document(result)

    inserted = db.shops.insert_one(update_doc)
    created = db.shops.find_one({"_id": inserted.inserted_id})
    return serialize_document(created)


def create_shop(payload: ShopCreateRequest) -> dict:
    db = get_db()

    shop_doc = {
        "name": payload.name,
        "settings": payload.settings.model_dump(),
        "is_active": True,
    }

    inserted = db.shops.insert_one(shop_doc)
    created = db.shops.find_one({"_id": inserted.inserted_id})
    return serialize_document(created)
