from typing import Optional
from bson import ObjectId
from app.database.connection import get_database
from app.models.user import User
from app.auth.utils import get_password_hash, verify_password
from app.schemas.user import UserCreate, UserUpdate

db = get_database()

class UserCRUD:
    @staticmethod
    def get_collection():
        return db["users"]

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        collection = UserCRUD.get_collection()
        user_data = await collection.find_one({"email": email})
        if user_data:
            return User.from_dict(user_data)
        return None

    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID"""
        collection = UserCRUD.get_collection()
        try:
            user_data = await collection.find_one({"_id": ObjectId(user_id)})
            if user_data:
                return User.from_dict(user_data)
        except:
            return None
        return None

    @staticmethod
    async def create_user(user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = await UserCRUD.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Create user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        
        collection = UserCRUD.get_collection()
        result = await collection.insert_one(user.to_dict())
        user._id = result.inserted_id
        return user

    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user = await UserCRUD.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    async def update_user(user_id: str, update_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        collection = UserCRUD.get_collection()
        
        # Prepare update data
        update_dict = {}
        if update_data.email is not None:
            update_dict["email"] = update_data.email
        if update_data.full_name is not None:
            update_dict["full_name"] = update_data.full_name
        
        if not update_dict:
            return None
        
        update_dict["updated_at"] = datetime.now(timezone.utc)
        
        result = await collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_dict}
        )
        
        if result.modified_count > 0:
            return await UserCRUD.get_user_by_id(user_id)
        return None

    @staticmethod
    async def delete_user(user_id: str) -> bool:
        """Delete a user"""
        collection = UserCRUD.get_collection()
        result = await collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0