from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    product_id: str
    quantity: int = Field(ge=1)


class OrderCreateRequest(BaseModel):
    table_id: str
    session_id: str
    items: list[OrderItem] = Field(min_length=1)
    notes: str | None = None
    status: str = "pending"


class OrderStatusUpdateRequest(BaseModel):
    status: str
