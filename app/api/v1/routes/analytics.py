#endpoints for analytics
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.schemas.analytics import AnalyticsSummary
from app.services import analytics_service

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

#analytics summary for the current logged in user
@router.get("/summary", response_model=AnalyticsSummary)
def get_my_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return analytics_service.get_user_analytics(db, current_user)

#platform wide analytics across all users for admin only
@router.get("/admin/summary", response_model=AnalyticsSummary)
def get_platform_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)  
):
    return analytics_service.get_platform_analytics(db)