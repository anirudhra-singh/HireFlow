#business logic for analytics
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.application import Application
from app.models.user import User
from app.schemas.analytics import AnalyticsSummary, StatusBreakdown


def _build_summary(db: Session, user_id=None) -> AnalyticsSummary:
    base_filter = [Application.is_deleted == False]
    if user_id is not None:
        base_filter.append(Application.user_id == user_id)

    total = db.query(Application).filter(*base_filter).count()

    status_counts = (
        db.query(Application.status, func.count(Application.id))
        .filter(*base_filter)
        .group_by(Application.status)
        .all()
    )

    breakdown = StatusBreakdown()
    for status_value, count in status_counts:
        setattr(breakdown, status_value.value, count)

    progressed = breakdown.interview + breakdown.offer
    conversion_rate = round((progressed / total * 100), 2) if total > 0 else 0.0

    return AnalyticsSummary(
        total_applications=total,
        status_breakdown=breakdown,
        conversion_rate=conversion_rate
    )

#for current logged-in user only
def get_user_analytics(db: Session, current_user: User) -> AnalyticsSummary:
    return _build_summary(db, user_id=current_user.id)

#for admin only no user filter
def get_platform_analytics(db: Session) -> AnalyticsSummary:
    return _build_summary(db, user_id=None)