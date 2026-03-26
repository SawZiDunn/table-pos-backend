# Table POS Backend

## MongoDB Atlas Setup

1. Copy `.env.example` to `.env`.
2. Replace `MONGODB_URI` with your MongoDB Atlas connection string.
3. Set `MONGODB_DB_NAME` to your target database name.

Install dependencies:

```bash
pip install -r requirements.txt
```

Use the connection in your app:

```python
from database import connect_db, close_db

db = connect_db()
# use db collections here

close_db()
```

`connect_db()` pings Atlas when creating the connection, so it will fail early if credentials or network access are incorrect.
