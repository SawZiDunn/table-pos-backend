import os

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException
from fastapi import UploadFile


CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
CLOUDINARY_FOLDER = os.getenv("CLOUDINARY_FOLDER", "products")


cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)


def _ensure_cloudinary_configured() -> None:
    if not CLOUDINARY_CLOUD_NAME or not CLOUDINARY_API_KEY or not CLOUDINARY_API_SECRET:
        raise HTTPException(status_code=500, detail="Cloudinary is not configured")


def upload_image(image_file: UploadFile) -> dict:
    _ensure_cloudinary_configured()

    try:
        result = cloudinary.uploader.upload(
            image_file.file,
            folder=CLOUDINARY_FOLDER,
            resource_type="image",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Image upload failed") from exc

    return {
        "url": result.get("secure_url") or result.get("url"),
        "public_id": result.get("public_id"),
    }


def delete_image(public_id: str) -> None:
    _ensure_cloudinary_configured()
    if not public_id:
        return

    try:
        cloudinary.uploader.destroy(public_id, resource_type="image")
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Image delete failed") from exc
