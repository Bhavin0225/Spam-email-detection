import pytest
from datetime import datetime, timezone, timedelta
from app.ml.feature_engine import FeatureExtractor
from app.database.collections import get_collection


def test_new_features_calculation(require_db):
    # Setup database records to test sender reputation
    emails_col = get_collection("emails")
    predictions_col = get_collection("predictions")

    emails_col.delete_many({})
    predictions_col.delete_many({})

    sender_domain = "scammer-domain.com"
    email_id_1 = "e-11"
    email_id_2 = "e-12"

    # Insert historical emails from same domain
    emails_col.insert_many([
        {
            "email_id": email_id_1,
            "sender_domain": sender_domain,
            "content_hash": "hash-1"
        },
        {
            "email_id": email_id_2,
            "sender_domain": sender_domain,
            "content_hash": "hash-2"
        }
    ])

    # Insert predictions (one suspicious, one legitimate -> spam ratio 0.5)
    predictions_col.insert_many([
        {
            "prediction_id": "p-11",
            "email_id": email_id_1,
            "prediction_label": "suspicious"
        },
        {
            "prediction_id": "p-12",
            "email_id": email_id_2,
            "prediction_label": "legitimate"
        }
    ])

    extractor = FeatureExtractor()
    
    # 1. Test sender reputation score (Features idx 16)
    test_email = {
        "subject": "Test",
        "body_text": "Hello",
        "sender": f"alert@{sender_domain}",
        "links": [],
        "headers": {},
        "date_sent": None,
        "attachments": []
    }
    
    features = extractor.extract_handcrafted_features(test_email)
    # The array has 20 features now. Index 16 is sender_reputation
    assert features[16] == 0.5

    # 2. Test email age (Features idx 17)
    yesterday = datetime.now(timezone.utc) - timedelta(hours=24)
    test_email["date_sent"] = yesterday
    features = extractor.extract_handcrafted_features(test_email)
    # email_age_hours should be approx 24
    assert 23.9 <= features[17] <= 24.1

    # 3. Test has attachments (Features idx 18)
    test_email["attachments"] = [{"filename": "invoice.pdf", "content_type": "application/pdf"}]
    features = extractor.extract_handcrafted_features(test_email)
    assert features[18] == 1.0
    # pdf risk = 0.3
    assert features[19] == 0.3

    # 4. Test attachment risk score (Features idx 19)
    test_email["attachments"] = [
        {"filename": "virus.exe", "content_type": "application/octet-stream"},
        {"filename": "document.docx", "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    ]
    features = extractor.extract_handcrafted_features(test_email)
    assert features[18] == 1.0
    # exe risk = 1.0 (max risk takes precedence)
    assert features[19] == 1.0
