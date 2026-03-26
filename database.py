import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database


load_dotenv()

_client: MongoClient | None = None
_database: Database | None = None


def connect_db() -> Database:
	"""Create a MongoDB client for Atlas and verify connectivity."""
	global _client, _database

	if _database is not None:
		return _database

	mongo_uri = os.getenv("MONGODB_URI")
	db_name = os.getenv("MONGODB_DB_NAME")

	if not mongo_uri:
		raise ValueError("MONGODB_URI is missing. Set it in your environment or .env file.")

	if not db_name:
		raise ValueError("MONGODB_DB_NAME is missing. Set it in your environment or .env file.")

	_client = MongoClient(mongo_uri)
	_client.admin.command("ping")
	_database = _client[db_name]
	return _database


def get_db() -> Database:
	"""Return the active MongoDB database instance."""
	if _database is None:
		return connect_db()
	return _database


def close_db() -> None:
	"""Close the active MongoDB connection if it exists."""
	global _client, _database

	if _client is not None:
		_client.close()
		_client = None
		_database = None
