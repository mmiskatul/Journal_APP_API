from pymongo import MongoClient
from app.config import settings

client = MongoClient(settings.MONGODB_URI)
db = client["journaling_db"]
users_collection = db["users"]

