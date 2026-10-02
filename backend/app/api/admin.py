from typing import List
from fastapi import Depends, APIRouter, BackgroundTasks, status
from app.core.permissions import require_admin
from app.database.crud import get_all_users
from app.schemas.auth import UserResponse
from app.schemas.feedback import FeedbackResponse, FeedbackStatusUpdate
from app.services.feedback_service import feedback_service
from app.database.collections import get_collection

router = APIRouter(prefix="/admin", tags=["Admin Operations"])

@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="List All Users",
    description="Retrieves registration profiles for all users. Restricted to admin or super_admin roles."
)
def list_users(admin_user: dict = Depends(require_admin)):
    """
    Returns lists of registered accounts. Restricted to administrators.
    """
    users = get_all_users()
    return users

@router.get(
    "/logs",
    summary="Get System Audit Logs",
    description="Retrieves the system logs collection. Restricted to administrators."
)
def list_logs(admin_user: dict = Depends(require_admin)):
    logs_col = get_collection("system_logs")
    logs = list(logs_col.find({}).sort("timestamp", -1).limit(100))
    for log in logs:
        if "_id" in log:
            log["_id"] = str(log["_id"])
    return logs

@router.get(
    "/feedback",
    response_model=List[FeedbackResponse],
    summary="List All Feedback corrections",
    description="Lists user prediction corrections. Restricted to administrators."
)
def list_feedback(admin_user: dict = Depends(require_admin)):
    return feedback_service.get_all_feedback()

@router.patch(
    "/feedback/{feedback_id}",
    response_model=FeedbackResponse,
    summary="Review correction feedback status",
    description="Approves or rejects a user prediction correction. If approved corrections reach 10+, triggers automated model retraining."
)
def review_feedback(
    feedback_id: str,
    body: FeedbackStatusUpdate,
    background_tasks: BackgroundTasks,
    admin_user: dict = Depends(require_admin)
):
    updated_fb = feedback_service.update_feedback_status(feedback_id, body.status)
    
    if updated_fb["status"] == "approved":
        # Check approved count
        fb_col = get_collection("feedback")
        approved_count = fb_col.count_documents({"status": "approved"})
        if approved_count >= 10:
            from app.ml.training import retrain_model_from_feedback
            background_tasks.add_task(retrain_model_from_feedback)
            
    return updated_fb

