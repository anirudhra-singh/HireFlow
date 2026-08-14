# requests and responses for job applications
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from app.models.application import ApplicationStatus

# request schemas
class ApplicationCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    job_title: str = Field(..., min_length=1, max_length=255)
    job_url: Optional[str] = Field(None, max_length=500)
    status: ApplicationStatus = ApplicationStatus.applied
    applied_date: date
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    job_title: Optional[str] = Field(None, min_length=1, max_length=255)
    job_url: Optional[str] = Field(None, max_length=500)
    status: Optional[ApplicationStatus] = None
    applied_date: Optional[date] = None
    notes: Optional[str] = None



# response schemas
class ApplicationResponse(BaseModel):
    id: UUID
    user_id: UUID
    company_name: str
    job_title: str
    job_url: Optional[str]
    status: ApplicationStatus
    applied_date: date
    notes: Optional[str]
    ai_tip: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationListResponse(BaseModel):
    total: int
    applications: list[ApplicationResponse]

# response generating by ai resume tip
class AITipResponse(BaseModel):
    application_id: UUID
    ai_tip: str
