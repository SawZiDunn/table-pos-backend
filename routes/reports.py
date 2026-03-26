from datetime import date

from fastapi import APIRouter, Query

from services.reports_service import get_daily_sales


router = APIRouter(tags=["reports"])


@router.get("/reports/daily-sales")
def get_daily_sales_api(shop_id: str = Query(...), target_date: date | None = Query(default=None)) -> dict:
    return get_daily_sales(shop_id, target_date)
