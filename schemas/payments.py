from pydantic import BaseModel, Field


class PaymentCreateRequest(BaseModel):
    shop_id: str
    order_id: str
    session_id: str
    amount: float = Field(gt=0)
    method: str = Field(min_length=1)
