from pydantic import BaseModel, Field


class ProductCreateRequest(BaseModel):
    category_id: str | None = None
    name: str = Field(min_length=1)
    price: float = Field(ge=0)
    is_available: bool = True


class ProductUpdateRequest(BaseModel):
    category_id: str | None = None
    name: str | None = None
    price: float | None = Field(default=None, ge=0)
    is_available: bool | None = None
