from datetime import datetime, timezone
from bson import ObjectId
from typing import Optional

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid object id")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class User:
    def __init__(
        self,
        email: str,
        full_name: str,
        hashed_password: str,
        is_active: bool = True,
        is_superuser: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id: Optional[PyObjectId] = None
    ):
        self._id = _id or ObjectId()
        self.email = email
        self.full_name = full_name
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.is_superuser = is_superuser
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    def to_dict(self):
        return {
            "_id": self._id,
            "email": self.email,
            "full_name": self.full_name,
            "hashed_password": self.hashed_password,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            _id=data.get("_id"),
            email=data["email"],
            full_name=data["full_name"],
            hashed_password=data["hashed_password"],
            is_active=data.get("is_active", True),
            is_superuser=data.get("is_superuser", False),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )