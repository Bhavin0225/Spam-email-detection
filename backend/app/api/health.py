from fastapi import APIRouter, HTTPException, status
from app.database.connection import db_manager
from app.schemas.common import HealthResponse, ErrorResponse
from app.utils.logger import logger

router = APIRouter()

@router.get(
    "/health",
    response_model=HealthResponse,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse}},
    summary="System Health Check",
    description="Verifies the operational status of the FastAPI backend and queries MongoDB Atlas connectivity."
)
def get_health():
    try:
        db_manager.ping()
        database_status = "connected"
    except Exception as e:
        logger.error(f"Health check failed due to database connection issue: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is unavailable."
        )

    return HealthResponse(
        status="ok",
        database=database_status
    )
