from fastapi import APIRouter, Depends, File, Form, Query, UploadFile

from services.auth_helpers import get_current_user
from services.products_service import create_product, delete_product, get_products, update_product

router = APIRouter(tags=["products"])

@router.get("/products")
def get_products_api(category_id: str | None = Query(default=None), current_user: dict = Depends(get_current_user)) -> list[dict]:
    return get_products(current_user.get("shop_id"), category_id)

@router.post("/products")
async def create_product_api(
    name: str = Form(...),
    price: float = Form(...),
    category_id: str | None = Form(default=None),
    is_available: bool = Form(default=True),
    image: UploadFile | None = File(default=None),
    current_user: dict = Depends(get_current_user),
) -> dict:
    
    return create_product(
        name,
        price,
        category_id,
        is_available,
        image,
        current_user.get("shop_id"),
    )


@router.put("/products/{id}")
def update_product_api(
    id: str,
    name: str | None = Form(default=None),
    price: float | None = Form(default=None),
    category_id: str | None = Form(default=None),
    is_available: bool | None = Form(default=None),
    image: UploadFile | None = File(default=None),
    current_user: dict = Depends(get_current_user),
) -> dict:
    return update_product(
        id,
        name,
        price,
        category_id,
        is_available,
        image,
        current_user.get("shop_id"),
    )


@router.delete("/products/{id}")
def delete_product_api(id: str, current_user: dict = Depends(get_current_user)) -> dict:
    return delete_product(id, current_user.get("shop_id"))
