from fastapi import APIRouter, Depends, Query

from schemas.products import ProductCreateRequest, ProductUpdateRequest
from services.auth_helpers import get_current_user
from services.products_service import create_product, delete_product, get_products, update_product

router = APIRouter(tags=["products"])

@router.get("/products")
def get_products_api(category_id: str | None = Query(default=None), current_user: dict = Depends(get_current_user)) -> list[dict]:
    return get_products(current_user.get("shop_id"), category_id)

@router.post("/products")
def create_product_api(payload: ProductCreateRequest, current_user: dict = Depends(get_current_user)) -> dict:
    return create_product(payload, current_user.get("shop_id"))


@router.put("/products/{id}")
def update_product_api(id: str, payload: ProductUpdateRequest, current_user: dict = Depends(get_current_user)) -> dict:
    return update_product(id, payload, current_user.get("shop_id"))


@router.delete("/products/{id}")
def delete_product_api(id: str, current_user: dict = Depends(get_current_user)) -> dict:
    return delete_product(id, current_user.get("shop_id"))
