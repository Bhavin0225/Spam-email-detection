import pytest
from pydantic import ValidationError
from datetime import datetime, timezone
from pydantic import ValidationError
from app.schemas.email import EmailInput
from app.schemas.prediction import PredictionResponse
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.schemas.analytics import AnalyticsResponse

def test_email_input_schema():
    # Valid
    inp = EmailInput(subject="Urgent", body="Verify login!", sender="attacker@scam.com")
    assert inp.subject == "Urgent"
    assert inp.body == "Verify login!"
    assert inp.sender == "attacker@scam.com"
    assert inp.headers is None

    # Missing field
    with pytest.raises(ValidationError):
        EmailInput(subject="Urgent", sender="attacker@scam.com")

def test_prediction_response_schema():
    # Valid
    resp = PredictionResponse(
        prediction_id="pred-123",
        email_id="email-456",
        prediction_label="suspicious",
        confidence=0.89,
        risk_level="high",
        model_version="v1.0.0",
        created_at=datetime.now(timezone.utc)
    )
    assert resp.prediction_id == "pred-123"
    assert resp.confidence == 0.89

def test_feedback_schemas():
    # FeedbackRequest validation
    req = FeedbackRequest(prediction_id="pred-123", was_correct=False, correct_label="ham")
    assert req.prediction_id == "pred-123"
    assert req.was_correct is False
    assert req.correct_label == "ham"

    # FeedbackResponse validation
    resp = FeedbackResponse(
        feedback_id="fb-123",
        prediction_id="pred-123",
        user_id="user-456",
        was_correct=False,
        correct_label="ham",
        comment="Legitimate letter",
        status="pending",
        created_at=datetime.now(timezone.utc)
    )
    assert resp.feedback_id == "fb-123"
    assert resp.user_id == "user-456"

def test_analytics_response_schema():
    # Valid
    resp = AnalyticsResponse(
        total_scans=150,
        spam_rate=0.45,
        false_positive_rate=0.02,
        predictions_over_time=[{"date": "2026-06-07", "total": 10, "spam": 4, "ham": 6}],
        top_suspicious_domains=[{"domain": "bad.com", "count": 25}]
    )
    assert resp.total_scans == 150
    assert resp.top_suspicious_domains[0]["domain"] == "bad.com"
