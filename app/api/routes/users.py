from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import Message
from app.schemas.user import ChangePasswordRequest, UserOut, UserProfileUpdate
from app.services import user as user_service

router = APIRouter()


@router.get("/me", response_model=UserOut)
def get_me(current_user=Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=UserOut)
def update_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    user = user_service.update_profile(db, current_user, payload.model_dump())
    return user


@router.post("/change-password", response_model=Message)
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    user_service.change_password(db, current_user, payload.current_password, payload.new_password)
    return Message(message="Password updated")
