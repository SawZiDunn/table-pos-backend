from pydantic import BaseModel


class AssignShopRequest(BaseModel):
    user_id: str
    shop_id: str
