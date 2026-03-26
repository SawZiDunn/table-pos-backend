from pydantic import BaseModel


class TableSessionCreateRequest(BaseModel):
    table_id: str
    shop_id: str
    opened_by: str | None = None
