from pydantic import BaseModel, Field


class TableCreateRequest(BaseModel):
    capacity: int = Field(ge=1)
    status: str = "available"
    shop_id: str = Field()


class TableUpdateRequest(BaseModel):
    capacity: int | None = Field(default=None, ge=1)
    status: str | None = None
    is_active: bool | None = None
