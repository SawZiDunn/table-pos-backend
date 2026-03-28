from fastapi import HTTPException

from database import get_db
from schemas.categories import CategoryCreateRequest
from services.mongo_helpers import BadObjectIdError, serialize_document, to_object_id


def get_categories(shop_id: str | None) -> list[dict]:
    if not shop_id:
        return []
        
    db = get_db()

    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    categories = db.categories.find({"shop_id": shop_obj_id})
    return [serialize_document(category) for category in categories]


def create_categories_bulk(payload: list[CategoryCreateRequest], shop_id: str | None) -> list[dict]:
    if not shop_id:
        raise HTTPException(status_code=400, detail="User does not have an assigned shop.")
        
    db = get_db()
    if not payload:
        return []

    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    category_docs = []
    for item in payload:
        category_docs.append({
            "shop_id": shop_obj_id,
            "name": item.name,
        })

    inserted = db.categories.insert_many(category_docs)
    created = db.categories.find({"_id": {"$in": inserted.inserted_ids}})
    return [serialize_document(cat) for cat in created]
