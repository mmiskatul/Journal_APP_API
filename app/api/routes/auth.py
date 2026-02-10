from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.core.database import get_db
from app.schemas.auth import ForgotPasswordRequest, RegisterRequest, ResetPasswordRequest
from app.schemas.common import Message, Token
from app.services import auth as auth_service
from app.services.audit import log_event

router = APIRouter()


@router.post("/register", response_model=Message)
def register(payload: RegisterRequest, db=Depends(get_db)):
    auth_service.register_user(db, payload.email, payload.password)
    return Message(message="Registered successfully")


@router.post("/login", response_model=Token)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    token = auth_service.create_login_token(user)

    log_event(
        db,
        user["id"],
        "login",
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )

    return Token(access_token=token)


@router.post("/forgot-password", response_model=Message)
def forgot_password(payload: ForgotPasswordRequest, db=Depends(get_db)):
    token = auth_service.start_password_reset(db, payload.email)
    if token:
        # In production, send the token via email.
        return Message(message=f"Reset token: {token}")
    return Message(message="If the email exists, a reset link has been sent")


@router.post("/reset-password", response_model=Message)
def reset_password(payload: ResetPasswordRequest, db=Depends(get_db)):
    auth_service.reset_password(db, payload.token, payload.new_password)
    return Message(message="Password reset successfully")
