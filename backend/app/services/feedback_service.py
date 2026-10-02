import uuid
from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.database.collections import get_collection
from app.schemas.feedback import FeedbackRequest
from app.utils.logger import logger

class FeedbackServiceClass:
    """
    Service responsible for storing user feedback, verifying prediction existence,
    verifying ownership, and validating input constraints.
    """
    def submit_feedback(self, feedback_req: FeedbackRequest, user_id: str) -> dict:
        """
        Validates prediction ownership/existence, applies structural constraints,
        and saves feedback to MongoDB feedback collection.
        """
        prediction_id = feedback_req.prediction_id
        was_correct = feedback_req.was_correct
        correct_label = (feedback_req.correct_label or "").strip().lower()
        comment = feedback_req.comment
        
        # 1. Validation: If was_correct is False, correct_label must be provided
        if not was_correct and not correct_label:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="correct_label is required when was_correct is False"
            )
            
        # 2. Check label correctness if label is provided
        valid_labels = {"legitimate", "suspicious", "ham", "spam"}
        if correct_label and correct_label not in valid_labels:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid correct_label. Must be one of {valid_labels}"
            )
            
        # 3. Verify target prediction exists in database
        predictions_col = get_collection("predictions")
        prediction = predictions_col.find_one({"prediction_id": prediction_id})
        if not prediction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prediction scan with ID '{prediction_id}' not found."
            )
            
        # 4. Enforce user ownership
        if prediction.get("user_id") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to submit feedback for this prediction scan."
            )
            
        # 5. Insert feedback record
        feedback_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        feedback_doc = {
            "feedback_id": feedback_id,
            "prediction_id": prediction_id,
            "user_id": user_id,
            "was_correct": was_correct,
            "correct_label": correct_label if not was_correct else (prediction.get("prediction_label") or ""),
            "comment": comment,
            "status": "pending",
            "created_at": now
        }
        
        feedback_col = get_collection("feedback")
        
        # Overwrite existing feedback for same prediction if any, or insert fresh
        feedback_col.delete_many({"prediction_id": prediction_id})
        feedback_col.insert_one(feedback_doc)
        logger.info(f"Feedback {feedback_id} recorded for prediction {prediction_id} by user {user_id}")
        
        # Format response
        if "_id" in feedback_doc:
            feedback_doc["_id"] = str(feedback_doc["_id"])
            
        return feedback_doc

    def get_all_feedback(self) -> list:
        """
        Retrieves all user correction feedback submissions.
        """
        feedback_col = get_collection("feedback")
        items = list(feedback_col.find({}).sort("created_at", -1))
        for item in items:
            if "_id" in item:
                item["_id"] = str(item["_id"])
        return items

    def update_feedback_status(self, feedback_id: str, new_status: str) -> dict:
        """
        Updates review status of a feedback correction submission.
        """
        new_status = new_status.strip().lower()
        if new_status not in {"approved", "rejected"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feedback status must be 'approved' or 'rejected'"
            )

        feedback_col = get_collection("feedback")
        feedback = feedback_col.find_one({"feedback_id": feedback_id})
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feedback correction with ID '{feedback_id}' not found."
            )

        feedback_col.update_one(
            {"feedback_id": feedback_id},
            {"$set": {"status": new_status, "updated_at": datetime.now(timezone.utc)}}
        )
        
        updated_doc = feedback_col.find_one({"feedback_id": feedback_id})
        if "_id" in updated_doc:
            updated_doc["_id"] = str(updated_doc["_id"])
        return updated_doc

# Singleton Instance
feedback_service = FeedbackServiceClass()
