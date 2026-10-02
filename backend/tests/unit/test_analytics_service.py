import pytest
from datetime import datetime, timezone
from app.database.collections import get_collection
from app.services.analytics_service import analytics_service

def test_analytics_empty_state(require_db):
    predictions_col = get_collection("predictions")
    feedback_col = get_collection("feedback")
    
    predictions_col.delete_many({})
    feedback_col.delete_many({})
    
    res = analytics_service.get_system_analytics()
    assert res["total_scans"] == 0
    assert res["spam_rate"] == 0.0
    assert res["false_positive_rate"] == 0.0
    assert len(res["predictions_over_time"]) == 0
    assert len(res["top_suspicious_domains"]) == 0

def test_analytics_calculation(require_db):
    predictions_col = get_collection("predictions")
    feedback_col = get_collection("feedback")
    emails_col = get_collection("emails")
    
    predictions_col.delete_many({})
    feedback_col.delete_many({})
    emails_col.delete_many({})
    
    now = datetime.now(timezone.utc)
    
    # Ingest emails
    emails_col.insert_many([
        {"email_id": "email-1", "sender_domain": "spam-domain.com", "content_hash": "h1"},
        {"email_id": "email-2", "sender_domain": "good-domain.com", "content_hash": "h2"},
        {"email_id": "email-3", "sender_domain": "spam-domain.com", "content_hash": "h3"}
    ])
    
    # Ingest predictions
    predictions_col.insert_many([
        {"prediction_id": "pred-1", "email_id": "email-1", "prediction_label": "suspicious", "confidence": 0.90, "risk_level": "high", "created_at": now},
        {"prediction_id": "pred-2", "email_id": "email-2", "prediction_label": "legitimate", "confidence": 0.10, "risk_level": "low", "created_at": now},
        {"prediction_id": "pred-3", "email_id": "email-3", "prediction_label": "suspicious", "confidence": 0.75, "risk_level": "medium", "created_at": now}
    ])
    
    # Ingest feedback
    feedback_col.insert_many([
        {"feedback_id": "fb-1", "prediction_id": "pred-1", "was_correct": False, "correct_label": "legitimate", "created_at": now},
        {"feedback_id": "fb-2", "prediction_id": "pred-2", "was_correct": True, "correct_label": "legitimate", "created_at": now}
    ])
    
    res = analytics_service.get_system_analytics()
    assert res["total_scans"] == 3
    assert res["spam_rate"] == pytest.approx(2 / 3)
    assert res["false_positive_rate"] == 0.5
    
    assert len(res["top_suspicious_domains"]) == 1
    assert res["top_suspicious_domains"][0]["domain"] == "spam-domain.com"
    assert res["top_suspicious_domains"][0]["count"] == 2
