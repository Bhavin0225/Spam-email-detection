import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.database.collections import get_collection
from app.core.security import create_access_token
from app.database.crud import create_user
from app.core.security import hash_password

def test_admin_feedback_endpoints_and_trigger(client: TestClient, require_db):
    """
    Checks GET /admin/feedback and PATCH /admin/feedback/{feedback_id} routes.
    Verifies RBAC enforcement and auto-retraining triggers.
    """
    user_email = "normal_user@example.com"
    admin_email = "admin_user@example.com"
    
    users_col = get_collection("users")
    users_col.delete_many({"email": {"$in": [user_email, admin_email]}})
    
    normal_usr = create_user(email=user_email, password_hash=hash_password("Pass123!"), role="user")
    admin_usr = create_user(email=admin_email, password_hash=hash_password("Pass123!"), role="admin")
    
    token_user = create_access_token(user_email, "user")
    token_admin = create_access_token(admin_email, "admin")
    
    headers_user = {"Authorization": f"Bearer {token_user}"}
    headers_admin = {"Authorization": f"Bearer {token_admin}"}
    
    predictions_col = get_collection("predictions")
    emails_col = get_collection("emails")
    feedback_col = get_collection("feedback")
    model_col = get_collection("model_metadata")
    
    predictions_col.delete_many({})
    emails_col.delete_many({})
    feedback_col.delete_many({})
    model_col.delete_many({})
    
    # Insert mock model metadata to prevent fallback crashes
    model_col.insert_one({
        "model_version": "v1.0.0",
        "algorithm": "XGBoost",
        "precision": 0.9,
        "recall": 0.9,
        "f1_score": 0.9,
        "auc_roc": 0.9,
        "threshold": 0.65,
        "deployed": True,
        "created_at": datetime.now(timezone.utc)
    })
    
    try:
        # Insert splits for retraining tests
        emails_col.insert_many([
            {"email_id": "email-1", "subject": "clean", "body_text": "legitimate email body text", "sender": "test@user.com", "sender_domain": "user.com", "links": [], "headers": {}, "content_hash": "hash1", "split": "train", "label": 0},
            {"email_id": "email-2", "subject": "spam", "body_text": "spam offer details", "sender": "spam@site.com", "sender_domain": "site.com", "links": [], "headers": {}, "content_hash": "hash2", "split": "validation", "label": 1},
            {"email_id": "email-3", "subject": "clean2", "body_text": "another email body", "sender": "test@user.com", "sender_domain": "user.com", "links": [], "headers": {}, "content_hash": "hash3", "split": "test", "label": 0},
        ])
        
        # 1. Access Check: Normal User GET /admin/feedback should block (403)
        response = client.get("/admin/feedback", headers=headers_user)
        assert response.status_code == 403
        
        # 2. Access Check: Admin GET /admin/feedback should allow (200)
        response = client.get("/admin/feedback", headers=headers_admin)
        assert response.status_code == 200
        assert len(response.json()) == 0
        
        # 3. Create mock prediction and feedback
        predictions_col.insert_one({
            "prediction_id": "pred-1",
            "email_id": "email-1",
            "prediction_label": "suspicious",
            "confidence": 0.88,
            "risk_level": "medium",
            "user_id": normal_usr["user_id"],
            "created_at": datetime.now(timezone.utc)
        })
        
        feedback_col.insert_one({
            "feedback_id": "fb-1",
            "prediction_id": "pred-1",
            "user_id": normal_usr["user_id"],
            "was_correct": False,
            "correct_label": "legitimate",
            "comment": "Report correction",
            "status": "pending",
            "created_at": datetime.now(timezone.utc)
        })
        
        # 4. Access Check: Normal User PATCH should block (403)
        payload = {"status": "approved"}
        response = client.patch("/admin/feedback/fb-1", json=payload, headers=headers_user)
        assert response.status_code == 403
        
        # 5. Access Check: Admin User PATCH updates status
        response = client.patch("/admin/feedback/fb-1", json=payload, headers=headers_admin)
        assert response.status_code == 200
        assert response.json()["status"] == "approved"
        
        # 6. Trigger Retraining threshold checks (need 10 approved items total)
        # Clear and insert 10 approved items to test trigger condition
        feedback_col.delete_many({})
        for i in range(10):
            predictions_col.insert_one({
                "prediction_id": f"pred-tr-{i}",
                "email_id": "email-1",
                "prediction_label": "suspicious",
                "confidence": 0.80,
                "user_id": normal_usr["user_id"],
                "created_at": datetime.now(timezone.utc)
            })
            feedback_col.insert_one({
                "feedback_id": f"fb-tr-{i}",
                "prediction_id": f"pred-tr-{i}",
                "user_id": normal_usr["user_id"],
                "was_correct": False,
                "correct_label": "legitimate",
                "status": "approved" if i < 9 else "pending", # Make 1 pending so last patch hits count == 10
                "created_at": datetime.now(timezone.utc)
            })
            
        # Patch the 10th one to hit 10 approved corrections
        response = client.patch("/admin/feedback/fb-tr-9", json=payload, headers=headers_admin)
        assert response.status_code == 200
        assert response.json()["status"] == "approved"
        
        # Check count is 10 approved
        count = feedback_col.count_documents({"status": "approved"})
        assert count == 10
    finally:
        import shutil
        import os
        from app.services.model_service import model_service
        
        # Delete the retrained version metadata and restore v1.0.0 as deployed
        model_col.delete_many({"model_version": "v1.1.0"})
        model_col.update_many({"model_version": "v1.0.0"}, {"$set": {"deployed": True}})
        
        # Delete generated model files from disk
        retrained_dir = os.path.join("models", "v1.1.0")
        if os.path.exists(retrained_dir):
            shutil.rmtree(retrained_dir)
            
        # Reset memory cache on the service to load original model on subsequent requests
        model_service._engine = None
        model_service._cached_version = None
