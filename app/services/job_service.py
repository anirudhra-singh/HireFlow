# app/services/job_service.py
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.application import Application
from app.models.user import User, UserRole
from app.schemas.application import ApplicationCreate, ApplicationUpdate
from app.services import ai_service

def create_application(
    db: Session,
    data: ApplicationCreate,
    current_user: User) -> Application:
    new_application = Application(
        user_id=current_user.id,
        company_name=data.company_name,
        job_title=data.job_title,
        job_url=data.job_url,
        status=data.status,
        applied_date=data.applied_date,
        notes=data.notes
    )
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    return new_application


def get_all_applications(
    db: Session,
    current_user: User) -> list[Application]:
    # admin sees all 
    if current_user.role == UserRole.admin:
        return db.query(Application).filter(
            Application.is_deleted == False
        ).all()

    return db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.is_deleted == False     
    ).all()


def get_application_by_id(
    db: Session,
    application_id: UUID,
    current_user: User) -> Application:
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.is_deleted == False).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    if current_user.role != UserRole.admin:
        if application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )

    return application


def update_application(
    db: Session,
    application_id: UUID,
    data: ApplicationUpdate,
    current_user: User) -> Application:
    application = get_application_by_id(db, application_id, current_user)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)

    db.commit()
    db.refresh(application)
    return application


def delete_application(
    db: Session,
    application_id: UUID,
    current_user: User) -> None:
    
    application = get_application_by_id(db, application_id, current_user)

    # soft delete 
    application.is_deleted = True
    db.commit()

#=== ai service
def generate_ai_tip(
    db: Session,
    application_id: UUID,
    current_user: User) -> Application:
    application = get_application_by_id(db, application_id, current_user)

    tip = ai_service.generate_resume_tip(
        company_name=application.company_name,
        job_title=application.job_title
    )

    application.ai_tip = tip
    db.commit()
    db.refresh(application)

    return application