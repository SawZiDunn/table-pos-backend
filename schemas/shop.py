from pydantic import BaseModel, Field


class ShopSettings(BaseModel):
    currency: str = Field(min_length=1)
    tax_percent: float = Field(default=0, ge=0, le=100)


class ShopUpsertRequest(BaseModel):
    id: str | None = None
    name: str = Field(min_length=1)
    address: str | None = None
    is_active: bool = True
    settings: ShopSettings | None = None


class ShopCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    settings: ShopSettings
