from pymongo import MongoClient
from app.config import settings

client = MongoClient(settings.MONGODB_URI)
db = client.get_database()  # Uses the database specified in the URI
users_collection = db["users"]
