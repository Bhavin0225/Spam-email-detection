from fastapi import APIRouter, Depends, status
from app.core.permissions import require_user
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.services.feedback_service import feedback_service

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit Prediction Correction Feedback",
    description="Logs user correction inputs to evaluate classifier precision and drift. Validates scan existence and ownership."
)
def submit_feedback(
    body: FeedbackRequest,
    current_user: dict = Depends(require_user)
):
    user_id = current_user["user_id"]
    feedback = feedback_service.submit_feedback(body, user_id)
    return feedback
