from fastapi import HTTPException
from pymongo import ReturnDocument

from database import get_db
from schemas.products import ProductCreateRequest, ProductUpdateRequest
from services.mongo_helpers import BadObjectIdError, serialize_document, to_object_id


def get_products(shop_id: str | None, category_id: str | None) -> list[dict]:
    if not shop_id:
        return []

    db = get_db()

    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    query: dict = {"shop_id": shop_obj_id}
    try:
        if category_id:
            query["category_id"] = to_object_id(category_id, "category_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    products = db.products.find(query)
    return [serialize_document(product) for product in products]


def create_product(payload: ProductCreateRequest, shop_id: str | None) -> dict:
    if not shop_id:
        raise HTTPException(status_code=400, detail="User does not have an assigned shop.")

    db = get_db()

    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    category_obj_id = None
    if payload.category_id:
        try:
            category_obj_id = to_object_id(payload.category_id, "category_id")
        except BadObjectIdError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid category_id: {str(exc)}") from exc

    product_doc = {
        "shop_id": shop_obj_id,
        "category_id": category_obj_id,
        "name": payload.name,
        "price": payload.price,
        "is_available": payload.is_available,
    }

    inserted = db.products.insert_one(product_doc)
    created = db.products.find_one({"_id": inserted.inserted_id})
    return serialize_document(created)


def update_product(product_id: str, payload: ProductUpdateRequest, shop_id: str | None) -> dict:
    if not shop_id:
        raise HTTPException(status_code=400, detail="User does not have an assigned shop.")
        
    db = get_db()

    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
        product_obj_id = to_object_id(product_id, "id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    updates = payload.model_dump(exclude_none=True)
    if "category_id" in updates and updates["category_id"]:
        try:
            updates["category_id"] = to_object_id(updates["category_id"], "category_id")
        except BadObjectIdError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated = db.products.find_one_and_update(
        {"_id": product_obj_id, "shop_id": shop_obj_id},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")

    return serialize_document(updated)


def delete_product(product_id: str, shop_id: str | None) -> dict:
    if not shop_id:
        raise HTTPException(status_code=400, detail="User does not have an assigned shop.")

    db = get_db()

    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
        product_obj_id = to_object_id(product_id, "id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = db.products.delete_one({"_id": product_obj_id, "shop_id": shop_obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"deleted_product_id": product_id}
