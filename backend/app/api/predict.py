from fastapi import APIRouter, Depends, status, Request
from app.core.permissions import require_user
from app.middleware.rate_limiter import limiter
from app.schemas.email import EmailInput
from app.schemas.prediction import PredictionResponse
from app.services.prediction_service import prediction_service

router = APIRouter(prefix="/predict", tags=["Predictions"])

@router.post(
    "",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict Email Label",
    description="Processes, vectorizes, and classifies email as 'suspicious' or 'legitimate' using active models. Rate limited to 10 requests per minute."
)
@limiter.limit("10/minute")
def predict(
    request: Request,
    body: EmailInput,
    current_user: dict = Depends(require_user)
):
    user_id = current_user["user_id"]
    prediction = prediction_service.predict_and_store(body, user_id)
    return prediction
