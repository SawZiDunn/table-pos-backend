from pydantic import BaseModel


class TableSessionCreateRequest(BaseModel):
    table_id: str
    opened_by: str | None = None
