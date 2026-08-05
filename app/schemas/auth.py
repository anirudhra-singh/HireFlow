# request/response shapes
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
from app.models.user import UserRole

# request schemas
# user register
class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr  
    password: str = Field(..., min_length=8, max_length=100)

# user login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

#client sends to get a new access token
class RefreshRequest(BaseModel):
    refresh_token: str

#client sends to logout
class LogoutRequest(BaseModel):
    refresh_token: str


# response schemas
class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"  

# returned after refresh token
class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str