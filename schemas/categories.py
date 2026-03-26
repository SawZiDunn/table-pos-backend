from pydantic import BaseModel, Field


class CategoryCreateRequest(BaseModel):
    shop_id: str
    name: str = Field(min_length=1)
