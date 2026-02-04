from pymongo import MongoClient
from pymongo.database import Database
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    client: MongoClient = None
    db: Database = None

    @classmethod
    def connect(cls):
        """Connect to MongoDB"""
        if cls.client is None:
            cls.client = MongoClient(os.getenv("MONGODB_URL"))
            cls.db = cls.client[os.getenv("MONGODB_DBNAME")]
        return cls.db

    @classmethod
    def disconnect(cls):
        """Disconnect from MongoDB"""
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.db = None

def get_database():
    """Dependency to get database instance"""
    return MongoDB.db