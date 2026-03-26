from datetime import date, datetime, time, timezone

from bson import ObjectId
from fastapi import HTTPException


class BadObjectIdError(ValueError):
    """Raised when a string is not a valid ObjectId."""


def to_object_id(value: str, field_name: str = "id") -> ObjectId:
    try:
        return ObjectId(value)
    except Exception as exc:
        raise BadObjectIdError(f"Invalid {field_name}: {value}") from exc


def normalize_http_error(exc: BadObjectIdError) -> HTTPException:
    return HTTPException(status_code=400, detail=str(exc))


def serialize_value(value: object) -> object:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return [serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    return value


def serialize_document(document: dict | None) -> dict | None:
    if not document:
        return document
    return {key: serialize_value(value) for key, value in document.items()}


def day_range_utc(day: date) -> tuple[datetime, datetime]:
    start = datetime.combine(day, time.min).replace(tzinfo=timezone.utc)
    end = datetime.combine(day, time.max).replace(tzinfo=timezone.utc)
    return start, end
