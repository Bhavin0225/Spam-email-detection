from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class FeedbackRequest(BaseModel):
    """
    Schema for user corrections/feedback on spam detections.
    """
    prediction_id: str = Field(..., description="The ID of the prediction being corrected")
    was_correct: bool = Field(..., description="Whether the ML model's prediction was correct")
    correct_label: str = Field(..., description="The user's correction label (e.g., 'legitimate', 'suspicious', 'ham', or 'spam')")
    comment: Optional[str] = Field(None, description="Optional description of the feedback context")

class FeedbackResponse(BaseModel):
    """
    Schema representing feedback stored in the database.
    """
    feedback_id: str = Field(..., description="Unique feedback identifier")
    prediction_id: str = Field(..., description="The prediction ID this correction belongs to")
    user_id: str = Field(..., description="The user who submitted this feedback")
    was_correct: bool = Field(..., description="Whether the prediction was flagged correct")
    correct_label: str = Field(..., description="Corrected target label")
    comment: Optional[str] = Field(None, description="User comment")
    status: str = Field("pending", description="Status of review, typically 'pending'")
    created_at: datetime = Field(..., description="Creation date")

class FeedbackStatusUpdate(BaseModel):
    """
    Schema for updating the review status of logged corrections.
    """
    status: str = Field(..., description="Target status ('approved' or 'rejected')")

