import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException

from database import get_db
from schemas.auth import LoginRequest
from services.mongo_helpers import serialize_document


JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def login(payload: LoginRequest) -> dict:
    db = get_db()
    user = db.users.find_one({"email": payload.email})

    if not user or user.get("password") != payload.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token_payload = {
        "sub": str(user["_id"]),
        "email": user["email"],
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=8),
    }
    access_token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": serialize_document(
            {
                "_id": user["_id"],
                "email": user.get("email"),
                "name": user.get("name"),
            }
        ),
    }
