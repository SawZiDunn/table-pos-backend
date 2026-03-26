from fastapi import HTTPException

from database import get_db
from schemas.categories import CategoryCreateRequest
from services.mongo_helpers import BadObjectIdError, serialize_document, to_object_id


def get_categories(shop_id: str) -> list[dict]:
    db = get_db()

    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    categories = db.categories.find({"shop_id": shop_obj_id})
    return [serialize_document(category) for category in categories]


def create_category(payload: CategoryCreateRequest) -> dict:
    db = get_db()

    try:
        shop_obj_id = to_object_id(payload.shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    category_doc = {
        "shop_id": shop_obj_id,
        "name": payload.name,
    }

    inserted = db.categories.insert_one(category_doc)
    created = db.categories.find_one({"_id": inserted.inserted_id})
    return serialize_document(created)
