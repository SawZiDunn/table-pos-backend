from typing import Literal

from pydantic import BaseModel


class TableSessionCreateRequest(BaseModel):
    table_id: str


class TableSessionCheckoutRequest(BaseModel):
    payment_method: Literal["cash", "card", "mobile_banking"]
