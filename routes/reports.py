from typing import Literal

from fastapi import APIRouter, Query, Depends

from services.auth_helpers import get_current_user
from services.reports_service import get_shop_summary

router = APIRouter(tags=["reports"])

@router.get("/reports/summary")
def get_shop_summary_api(
    period: Literal["today", "week", "month", "all_time"] = Query(default="today"),
    current_user: dict = Depends(get_current_user)
) -> dict:
    return get_shop_summary(current_user.get("shop_id"), period)
