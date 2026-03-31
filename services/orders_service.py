from datetime import datetime, timezone

from fastapi import HTTPException
from pymongo import ReturnDocument

from database import get_db
from schemas.orders import OrderCreateRequest
from services.mongo_helpers import BadObjectIdError, serialize_document, to_object_id


VALID_ORDER_STATUSES = {"pending", "preparing", "served", "cancelled"}


def create_order(payload: OrderCreateRequest, shop_id: str | None) -> dict:
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing shop_id for current user")
        
    db = get_db()

    try:
        shop_obj_id = to_object_id(shop_id, "shop_id")
        table_obj_id = to_object_id(payload.table_id, "table_id")
        session_obj_id = to_object_id(payload.session_id, "session_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    session = db.table_sessions.find_one({"_id": session_obj_id, "shop_id": shop_obj_id, "status": "open"})
    if not session:
        raise HTTPException(status_code=404, detail="Open session not found")

    items_payload = payload.items
    product_ids = []
    for item in items_payload:
        try:
            product_ids.append(to_object_id(item.product_id, "product_id"))
        except BadObjectIdError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid product_id: {item.product_id}") from exc

    # Fetch all requested products that belong to this shop securely
    products_cursor = db.products.find({"_id": {"$in": product_ids}, "shop_id": shop_obj_id})
    products_map = {str(p["_id"]): p for p in products_cursor}

    processed_items = []
    total_amount = 0.0

    for item in items_payload:
        product_str_id = item.product_id
        if product_str_id not in products_map:
            raise HTTPException(status_code=400, detail=f"Product {product_str_id} not found in your shop")
            
        real_product = products_map[product_str_id]
        
        if not real_product.get("is_available", True):
            raise HTTPException(status_code=400, detail=f"Product '{real_product['name']}' is currently unavailable")

        qty = item.quantity
        price = real_product["price"]
        total_amount += (qty * price)

        processed_items.append({
            "product_id": str(real_product["_id"]),
            "name": real_product["name"],
            "unit_price": price,
            "quantity": qty
        })

    order_doc = {
        "shop_id": shop_obj_id,
        "table_id": table_obj_id,
        "session_id": session_obj_id,
        "items": processed_items,
        "notes": payload.notes,
        "status": payload.status,
        "total_amount": total_amount,
        "created_at": datetime.now(tz=timezone.utc),
    }

    inserted = db.orders.insert_one(order_doc)
    created = db.orders.find_one({"_id": inserted.inserted_id})
    return serialize_document(created)


def get_orders(shop_id: str | None, session_id: str | None, status: str | None) -> list[dict]:
    if not shop_id:
        return []
        
    db = get_db()
    query: dict = {}

    try:
        if shop_id:
            query["shop_id"] = to_object_id(shop_id, "shop_id")
        if session_id:
            query["session_id"] = to_object_id(session_id, "session_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if status:
        query["status"] = status

    orders = db.orders.find(query).sort("created_at", -1)
    return [serialize_document(order) for order in orders]


def update_order_status(order_id: str, status: str, shop_id: str | None) -> dict:
    if not shop_id:
        raise HTTPException(status_code=400, detail="Missing shop_id for current user")
        
    db = get_db()

    if status not in VALID_ORDER_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid order status")

    try:
        order_obj_id = to_object_id(order_id, "id")
        shop_obj_id = to_object_id(shop_id, "shop_id")
    except BadObjectIdError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if status == "cancelled":
        existing = db.orders.find_one({"_id": order_obj_id, "shop_id": shop_obj_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Order not found")
        if existing.get("status") != "pending":
            raise HTTPException(status_code=400, detail="Order is already being prepared")

    updated = db.orders.find_one_and_update(
        {"_id": order_obj_id, "shop_id": shop_obj_id},
        {"$set": {"status": status}},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")

    return serialize_document(updated)
