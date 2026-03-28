from fastapi import FastAPI

from database import close_db, connect_db
from routes.auth import router as auth_router
from routes.categories import router as categories_router
from routes.orders import router as orders_router
from routes.products import router as products_router
from routes.reports import router as reports_router
from routes.shop import router as shop_router
from routes.table_sessions import router as table_sessions_router
from routes.tables import router as tables_router


app = FastAPI(title="Table POS Backend", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    connect_db()


@app.on_event("shutdown")
def shutdown() -> None:
    close_db()


app.include_router(auth_router)
app.include_router(shop_router)
app.include_router(tables_router)
app.include_router(table_sessions_router)
app.include_router(orders_router)
app.include_router(products_router)
app.include_router(categories_router)
app.include_router(reports_router)
