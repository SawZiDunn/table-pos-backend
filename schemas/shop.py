from pydantic import BaseModel, Field


class ShopUpsertRequest(BaseModel):
    id: str | None = None
    user_id: str
    name: str = Field(min_length=1)
    address: str | None = None
    is_active: bool = True
