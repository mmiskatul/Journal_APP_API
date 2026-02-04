from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import UserCreate, UserResponse, TokenResponse
from app.crud import user as crud
from app.auth import auth_handler
from fastapi import Request

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate):
    if crud.get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = crud.create_user(user.username, user.email, user.password)
    return UserResponse(
        id=new_user["_id"],
        username=new_user["username"],
        email=new_user["email"],
        created_at=new_user["created_at"],
        is_active=new_user["is_active"]
    )

@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.get_user_by_email(form_data.username)
    if not user or not auth_handler.verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth_handler.create_access_token(str(user["_id"]))
    return TokenResponse(access_token=token)

@router.get("/me", response_model=UserResponse)
def get_me(token: str = Depends(OAuth2PasswordRequestForm)):
    user_id = auth_handler.decode_token(token)
    user = crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        created_at=user["created_at"],
        is_active=user["is_active"]
    )
