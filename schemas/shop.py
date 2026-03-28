from pydantic import BaseModel, Field


class ShopSettings(BaseModel):
    currency: str = Field(min_length=1)


class ShopUpsertRequest(BaseModel):
    id: str | None = None
    name: str = Field(min_length=1)
    address: str | None = None
    is_active: bool = True


class ShopCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    settings: ShopSettings
