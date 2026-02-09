from pymongo import MongoClient

from app.core.config import settings

client = MongoClient(settings.mongodb_uri)
db = client[settings.mongodb_dbname]


def get_db():
    return db
