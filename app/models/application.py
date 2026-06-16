# every job application a user tracks lives here

import uuid
from sqlalchemy import Column, String, Text, Date, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ApplicationStatus(str, enum.Enum):
    applied = "applied"
    interview = "interview"
    offer = "offer"
    rejected = "rejected"
    withdrawn = "withdrawn"


class Application(Base):
    __tablename__ = "applications"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True  
    )

    company_name = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    job_url = Column(String(500), nullable=True)

    status = Column(
        SQLEnum(ApplicationStatus),
        default=ApplicationStatus.applied,
        nullable=False
    )

    applied_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)

    # ai_tip stores the gemini ai advice for this application
    ai_tip = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # relationship back to User
    user = relationship("User", back_populates="applications")

    def __repr__(self):
        return f"<Application {self.company_name} - {self.job_title}>"