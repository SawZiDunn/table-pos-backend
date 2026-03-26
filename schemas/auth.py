from typing import Literal

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    shop_id: str


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Literal["manager", "staff"] = "staff"
