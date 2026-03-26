from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    product_id: str | None = None
    name: str
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0)


class OrderCreateRequest(BaseModel):
    shop_id: str
    table_id: str
    session_id: str
    items: list[OrderItem] = Field(min_length=1)
    notes: str | None = None
    status: str = "pending"


class OrderStatusUpdateRequest(BaseModel):
    status: str
