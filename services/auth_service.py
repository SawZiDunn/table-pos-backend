import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException
import bcrypt

from database import get_db
from schemas.auth import LoginRequest, RegisterRequest
from services.mongo_helpers import BadObjectIdError, serialize_document, to_object_id


JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def _build_access_token(user: dict, shop_id: str | None = None) -> str:
    token_payload = {
        "sub": str(user["_id"]),
        "email": user["email"],
        "role": user.get("role", "staff"),
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=8),
    }
    if shop_id:
        token_payload["shop_id"] = shop_id
    return jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _serialize_user(user: dict, shop_id: str | None = None) -> dict:
    serialized = {
        "_id": user["_id"],
        "email": user.get("email"),
        "name": user.get("name"),
        "role": user.get("role", "staff"),
    }
    if shop_id:
        serialized["shop_id"] = shop_id
    return serialize_document(
        serialized
    )


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def _ensure_password_length(password: str) -> None:
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password too long (max 72 bytes).",
        )


def login(payload: LoginRequest) -> dict:
    db = get_db()
    user = db.users.find_one({"email": payload.email})

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    _ensure_password_length(payload.password)

    stored_password = user.get("password", "")
    is_password_valid = _verify_password(payload.password, stored_password)
    if not is_password_valid and stored_password == payload.password:
        # Legacy fallback for unhashed passwords; re-hash on success.
        is_password_valid = True
        db.users.update_one(
            {"_id": user["_id"]}, {"$set": {"password": _hash_password(payload.password)}}
        )

    if not is_password_valid:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if payload.role and user.get("role") != payload.role:
        raise HTTPException(status_code=401, detail="Mismatched Role Information")

    shop_id_raw = user.get("shop_id")
    shop_id_str = str(shop_id_raw) if shop_id_raw else None

    if shop_id_raw:
        try:
            shop_obj_id = to_object_id(shop_id_raw, "shop_id")
        except BadObjectIdError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
            
        shop = db.shops.find_one({"_id": shop_obj_id, "is_active": True})
        if not shop:
            raise HTTPException(status_code=404, detail="Assigned shop not found or inactive")

    return {
        "access_token": _build_access_token(user, shop_id_str),
        "token_type": "bearer",
        "user": _serialize_user(user, shop_id_str),
    }


def register(payload: RegisterRequest) -> dict:
    db = get_db()
    existing_user = db.users.find_one({"email": payload.email})
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    _ensure_password_length(payload.password)

    user_doc = {
        "name": payload.name,
        "email": payload.email,
        "password": _hash_password(payload.password),
        "role": payload.role,
        "created_at": datetime.now(tz=timezone.utc),
    }
    print("user_doc", user_doc)
    insert_result = db.users.insert_one(user_doc)
    user_doc["_id"] = insert_result.inserted_id

    return {
        "access_token": _build_access_token(user_doc),
        "token_type": "bearer",
        "user": _serialize_user(user_doc),
    }


def logout(current_user: dict) -> dict:
    return {
        "message": "Logged out successfully",
        "user_id": current_user.get("id"),
    }
