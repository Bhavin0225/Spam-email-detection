from fastapi import APIRouter, Depends
from app.core.permissions import require_analyst
from app.schemas.analytics import AnalyticsResponse
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get(
    "",
    response_model=AnalyticsResponse,
    summary="Get System Classification Statistics",
    description="Aggregates system scan volumes, false-positive metrics, daily time-series counts, and suspicious sender domains. Requires Analyst role or above."
)
def get_analytics(current_user: dict = Depends(require_analyst)):
    return analytics_service.get_system_analytics()
