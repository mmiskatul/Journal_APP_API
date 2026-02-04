from app.database import users_collection
from app.auth.auth_handler import hash_password
from bson.objectid import ObjectId
from datetime import datetime

def create_user(username: str, email: str, password: str):
    hashed_pw = hash_password(password)
    user_doc = {
        "username": username,
        "email": email,
        "password": hashed_pw,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    result = users_collection.insert_one(user_doc)
    user_doc["_id"] = str(result.inserted_id)
    return user_doc

def get_user_by_email(email: str):
    return users_collection.find_one({"email": email})

def get_user_by_id(user_id: str):
    return users_collection.find_one({"_id": ObjectId(user_id)})
