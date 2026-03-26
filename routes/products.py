from fastapi import APIRouter, Query

from schemas.products import ProductCreateRequest, ProductUpdateRequest
from services.products_service import create_product, get_products, update_product


router = APIRouter(tags=["products"])


@router.get("/products")
def get_products_api(shop_id: str = Query(...), category_id: str | None = Query(default=None)) -> list[dict]:
    return get_products(shop_id, category_id)


@router.post("/products")
def create_product_api(payload: ProductCreateRequest) -> dict:
    return create_product(payload)


@router.put("/products/{id}")
def update_product_api(id: str, payload: ProductUpdateRequest) -> dict:
    return update_product(id, payload)
