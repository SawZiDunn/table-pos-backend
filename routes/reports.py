from datetime import date

from fastapi import APIRouter, Query

from services.reports_service import (
    get_daily_sales,
    get_monthly_sales,
    get_daily_orders_summary,
    get_session_summary,
    get_table_summary,
)


router = APIRouter(tags=["reports"])


@router.get("/reports/daily-sales")
def get_daily_sales_api(shop_id: str = Query(...), target_date: date | None = Query(default=None)) -> dict:
    return get_daily_sales(shop_id, target_date)


@router.get("/reports/monthly-sales")
def get_monthly_sales_api(shop_id: str = Query(...), year: int = Query(...), month: int = Query(...)) -> dict:
    return get_monthly_sales(shop_id, year, month)


@router.get("/reports/daily-orders")
def get_daily_orders_api(shop_id: str = Query(...), target_date: date | None = Query(default=None)) -> dict:
    return get_daily_orders_summary(shop_id, target_date)


@router.get("/reports/session")
def get_session_summary_api(session_id: str = Query(...)) -> dict:
    return get_session_summary(session_id)


@router.get("/reports/table")
def get_table_summary_api(shop_id: str = Query(...), table_id: str = Query(...)) -> dict:
    return get_table_summary(shop_id, table_id)
