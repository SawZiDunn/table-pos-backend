# Table POS Backend

FastAPI backend for a table-based POS system using MongoDB Atlas.

## MongoDB Atlas Setup

1. Copy `.env.example` to `.env`.
2. Replace `MONGODB_URI` with your MongoDB Atlas connection string.
3. Set `MONGODB_DB_NAME` to your target database name.

Install dependencies:

```bash
pip install -r requirements.txt
```

Run server:

```bash
uvicorn main:app --reload
```

Use the connection in your app:

```python
from database import connect_db, close_db

db = connect_db()
# use db collections here

close_db()
```

`connect_db()` pings Atlas when creating the connection, so it will fail early if credentials or network access are incorrect.

## API Endpoints

- `POST /auth/login`
- `GET /shop`
- `PUT /shop`
- `GET /tables`
- `POST /tables`
- `PUT /tables/{id}`
- `POST /table-sessions`
- `GET /table-sessions/open`
- `POST /orders`
- `GET /orders`
- `PUT /orders/{id}/status`
- `GET /products`
- `POST /products`
- `PUT /products/{id}`
- `GET /categories`
- `POST /categories`
- `POST /payments`
- `GET /reports/daily-sales`

## Current Domain Flow

- One user can have multiple shops.
- One shop has many tables.
- One table has many table sessions.
- One table session has many orders.
