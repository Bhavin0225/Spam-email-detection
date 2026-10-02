import pytest
from datetime import datetime, timezone
from fastapi import HTTPException
from app.database.collections import get_collection
from app.services.feedback_service import feedback_service
from app.schemas.feedback import FeedbackRequest

def test_feedback_submission_missing_prediction(require_db):
    req = FeedbackRequest(prediction_id="nonexistent-id", was_correct=True, correct_label="")
    with pytest.raises(HTTPException) as exc:
        feedback_service.submit_feedback(req, user_id="user-1")
    assert exc.value.status_code == 404

def test_feedback_submission_invalid_label_or_missing_constraints(require_db):
    # was_correct is False, but correct_label is empty -> 422
    req = FeedbackRequest(prediction_id="pred-123", was_correct=False, correct_label="")
    with pytest.raises(HTTPException) as exc:
        feedback_service.submit_feedback(req, user_id="user-1")
    assert exc.value.status_code == 422

    # incorrect label string -> 422
    req = FeedbackRequest(prediction_id="pred-123", was_correct=False, correct_label="invalid_label")
    with pytest.raises(HTTPException) as exc:
        feedback_service.submit_feedback(req, user_id="user-1")
    assert exc.value.status_code == 422

def test_feedback_submission_permission_check(require_db):
    predictions_col = get_collection("predictions")
    predictions_col.delete_many({})
    predictions_col.insert_one({
        "prediction_id": "pred-1",
        "user_id": "user-owner",
        "prediction_label": "suspicious",
        "confidence": 0.90,
        "risk_level": "high",
        "created_at": datetime.now(timezone.utc)
    })

    # Try to submit feedback with user-other -> 403
    req = FeedbackRequest(prediction_id="pred-1", was_correct=True, correct_label="")
    with pytest.raises(HTTPException) as exc:
        feedback_service.submit_feedback(req, user_id="user-other")
    assert exc.value.status_code == 403

    # Try with user-owner -> succeeds and inserts record
    req = FeedbackRequest(prediction_id="pred-1", was_correct=False, correct_label="legitimate")
    fb = feedback_service.submit_feedback(req, user_id="user-owner")
    assert fb["status"] == "pending"
    assert fb["was_correct"] is False
    assert fb["correct_label"] == "legitimate"
