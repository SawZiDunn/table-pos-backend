from pydantic import BaseModel, Field


class TableCreateRequest(BaseModel):
    table_number: int = Field(ge=1)
    capacity: int = Field(ge=1)
    status: str = "available"


class TableUpdateRequest(BaseModel):
    capacity: int | None = Field(default=None, ge=1)
    status: str | None = None
    is_active: bool | None = None
