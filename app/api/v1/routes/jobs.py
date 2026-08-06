#http endpoints for job applications
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationListResponse
)
from app.services import job_service

router = APIRouter(prefix="/api/v1/jobs", tags=["Job Applications"])


@router.post("/",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_application(
    data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return job_service.create_application(db, data, current_user)


@router.get("/", response_model=ApplicationListResponse)
def get_all_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    applications = job_service.get_all_applications(db, current_user)
    return ApplicationListResponse(
        total=len(applications),
        applications=applications
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return job_service.get_application_by_id(db, application_id, current_user)


@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: UUID,
    data: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return job_service.update_application(db, application_id, data, current_user)


@router.delete(
    "/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT 
)
def delete_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job_service.delete_application(db, application_id, current_user)