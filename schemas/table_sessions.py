from typing import Literal

from pydantic import BaseModel, Field


class TableSessionCreateRequest(BaseModel):
    table_id: str


class TableSessionCheckoutRequest(BaseModel):
    payment_method: Literal["cash", "card", "mobile_banking"]


class TableSessionGuestCountUpdateRequest(BaseModel):
    guest_count: int = Field(ge=0)
