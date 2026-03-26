from fastapi import APIRouter

from schemas.payments import PaymentCreateRequest
from services.payments_service import create_payment


router = APIRouter(tags=["payments"])


@router.post("/payments")
def create_payment_api(payload: PaymentCreateRequest) -> dict:
    return create_payment(payload)
