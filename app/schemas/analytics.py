from pydantic import BaseModel


class StatusBreakdown(BaseModel):
    applied: int = 0
    interview: int = 0
    offer: int = 0
    rejected: int = 0
    withdrawn: int = 0


class AnalyticsSummary(BaseModel):
    total_applications: int
    status_breakdown: StatusBreakdown
    conversion_rate: float  # percentage rate