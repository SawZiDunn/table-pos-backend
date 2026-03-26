from pydantic import BaseModel, Field


class TableCreateRequest(BaseModel):
    shop_id: str
    name: str = Field(min_length=1)
    capacity: int = Field(ge=1)
    status: str = "available"


class TableUpdateRequest(BaseModel):
    name: str | None = None
    capacity: int | None = Field(default=None, ge=1)
    status: str | None = None
    is_active: bool | None = None
