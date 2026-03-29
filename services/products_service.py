from fastapi import HTTPException, UploadFile
from pymongo import ReturnDocument

from database import get_db
from services.mongo_helpers import BadObjectIdError, serialize_document, to_object_id
from services.cloudinary_service import delete_image, upload_image


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


def create_product(
    name: str,
    price: float,
    category_id: str | None,
    is_available: bool,
    image_file: UploadFile | None,
    shop_id: str | None,
) -> dict:
    if not shop_id:
        raise HTTPException(status_code=400, detail="User does not have an assigned shop.")

    if not image_file:
        raise HTTPException(status_code=400, detail="Image is required")

    db = get_db()

    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    category_obj_id = None
    if category_id:
        try:
            category_obj_id = to_object_id(category_id, "category_id")
        except BadObjectIdError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid category_id: {str(exc)}") from exc

    upload_result = upload_image(image_file)
    if not upload_result.get("url") or not upload_result.get("public_id"):
        raise HTTPException(status_code=500, detail="Image upload failed")

    product_doc = {
        "shop_id": shop_obj_id,
        "category_id": category_obj_id,
        "name": name,
        "price": price,
        "is_available": is_available,
        "image_url": upload_result["url"],
        "image_public_id": upload_result["public_id"],
    }

    inserted = db.products.insert_one(product_doc)
    created = db.products.find_one({"_id": inserted.inserted_id})
    return serialize_document(created)


def update_product(
    product_id: str,
    name: str | None,
    price: float | None,
    category_id: str | None,
    is_available: bool | None,
    image_file: UploadFile | None,
    shop_id: str | None,
) -> dict:
    if not shop_id:
        raise HTTPException(status_code=400, detail="User does not have an assigned shop.")
        
    db = get_db()

    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
        product_obj_id = to_object_id(product_id, "id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    existing_product = db.products.find_one({"_id": product_obj_id, "shop_id": shop_obj_id})
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")

    updates: dict = {}
    if name is not None:
        updates["name"] = name
    if price is not None:
        updates["price"] = price
    if is_available is not None:
        updates["is_available"] = is_available
    if category_id is not None:
        try:
            updates["category_id"] = to_object_id(category_id, "category_id")
        except BadObjectIdError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    if image_file is not None:
        upload_result = upload_image(image_file)
        if not upload_result.get("url") or not upload_result.get("public_id"):
            raise HTTPException(status_code=500, detail="Image upload failed")
        old_public_id = existing_product.get("image_public_id")
        if old_public_id:
            delete_image(old_public_id)
        updates["image_url"] = upload_result["url"]
        updates["image_public_id"] = upload_result["public_id"]

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated = db.products.find_one_and_update(
        {"_id": product_obj_id, "shop_id": shop_obj_id},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
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

    product = db.products.find_one({"_id": product_obj_id, "shop_id": shop_obj_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    public_id = product.get("image_public_id")
    if public_id:
        delete_image(public_id)

    result = db.products.delete_one({"_id": product_obj_id, "shop_id": shop_obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"deleted_product_id": product_id}
