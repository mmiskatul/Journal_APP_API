from datetime import timedelta
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database.connection import MongoDB
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, 
    UserUpdate, Token, UserInDB
)
from app.crud.user import UserCRUD
from app.auth.utils import create_access_token, verify_password
from app.auth.dependencies import get_current_user
from app.models.user import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    MongoDB.connect()
    print("Connected to MongoDB")
    yield
    # Shutdown
    MongoDB.disconnect()
    print("Disconnected from MongoDB")

app = FastAPI(
    title="FastAPI Authentication System",
    description="Complete authentication system with MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user
    """
    try:
        user = await UserCRUD.create_user(user_data)
        return UserResponse(
            id=str(user._id),
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )

@app.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """
    Login user and return access token
    """
    user = await UserCRUD.authenticate_user(login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return UserResponse(
        id=str(current_user._id),
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

@app.put("/me", response_model=UserResponse)
async def update_user_info(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update current user information
    """
    updated_user = await UserCRUD.update_user(str(current_user._id), update_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update failed"
        )
    
    return UserResponse(
        id=str(updated_user._id),
        email=updated_user.email,
        full_name=updated_user.full_name,
        is_active=updated_user.is_active,
        created_at=updated_user.created_at
    )

@app.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(current_user: User = Depends(get_current_user)):
    """
    Delete current user account
    """
    success = await UserCRUD.delete_user(str(current_user._id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete account"
        )

# Health check
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "database": "connected"}