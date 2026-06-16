import uuid
import enum
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,  
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,        
        nullable=False,     
        index=True          
    )

    
    hashed_password = Column(
        String(255),
        nullable=False
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    role = Column(
        SQLEnum(UserRole),
        default=UserRole.user,  
        nullable=False
    )

  
    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

 
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),  # auto updates when record changes
        nullable=False
    )


    applications = relationship(
        "Application",
        back_populates="user",
        cascade="all, delete-orphan"  
    )

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"