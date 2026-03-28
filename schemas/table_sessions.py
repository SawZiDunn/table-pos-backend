from pydantic import BaseModel


class TableSessionCreateRequest(BaseModel):
    table_id: str
