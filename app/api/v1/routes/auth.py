# http endpoints for authentication
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    LogoutRequest,
    UserResponse,
    TokenResponse,
    AccessTokenResponse,
    MessageResponse
)
from app.services import auth_service
from app.models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED  
)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = auth_service.register_user(db, data)
    return user

#login and receive access and refresh tokens
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    tokens = auth_service.login_user(db, data)
    return TokenResponse(**tokens)

#get new access token using refresh token
@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    access_token = auth_service.refresh_access_token(db, data.refresh_token)
    return AccessTokenResponse(access_token=access_token)


#logout by revoking refresh token
@router.post("/logout", response_model=MessageResponse)
def logout(data: LogoutRequest, db: Session = Depends(get_db)):
    auth_service.logout_user(db, data.refresh_token)
    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user