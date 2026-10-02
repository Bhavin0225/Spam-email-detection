import uuid
import re
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pymongo.errors import DuplicateKeyError
from app.database.collections import get_collection
from app.utils.hashing import calculate_content_hash
from app.services.model_service import model_service
from app.schemas.email import EmailInput
from app.ml.feature_engine import extract_email_address
from app.utils.logger import logger

TRUSTED_DOMAINS = {
    "google.com",
    "accounts.google.com",
    "youtube.com",
    "canarabank.com",
    "canarabank.in",
    "pinterest.com",
    "ideas.pinterest.com",
    "zerodha.net",
    "reportsmailer.zerodha.net",
    "github.com",
    "microsoft.com",
    "apple.com",
    "amazon.com",
    "linkedin.com",
    "bankofamerica.com",
    "chase.com",
    "wellsfargo.com",
    "citi.com"
}

class PredictionServiceClass:
    """
    Service to orchestrate incoming predict tasks, deduplicate matching email
    contents, register prediction runs, and look up scan history records.
    """
    def predict_and_store(self, email_input: EmailInput, user_id: str) -> dict:
        """
        Parses raw text, deduplicates email document, executes model inference,
        stores prediction details, and returns PredictionResponse contents.
        """
        subject = email_input.subject
        body = email_input.body
        sender = email_input.sender
        
        # 1. Parse details
        sender_email = extract_email_address(sender)
        sender_domain = sender_email.split("@")[-1].lower() if "@" in sender_email else sender_email.lower()
        
        # URL link extraction
        links = re.findall(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", body)
        
        # Headers extraction and fallback defaults
        input_headers = email_input.headers or {}
        headers = {
            "spf": input_headers.get("spf", "") or "",
            "dkim": input_headers.get("dkim", "") or "",
            "dmarc": input_headers.get("dmarc", "") or "",
            "reply-to": input_headers.get("reply-to", "") or "",
            "hop_count": int(input_headers.get("hop_count", 0))
        }
        
        # Calculate content hash for unique content check
        content_hash = calculate_content_hash(subject, body)
        
        emails_col = get_collection("emails")
        
        # Deduplication search
        email_record = emails_col.find_one({"content_hash": content_hash})
        
        if email_record:
            email_id = email_record["email_id"]
            logger.info(f"Duplicate email found in database. Re-using email_id: {email_id}")
        else:
            email_id = str(uuid.uuid4())
            new_email = {
                "email_id": email_id,
                "subject": subject,
                "sender": sender,
                "sender_domain": sender_domain,
                "body_text": body,
                "links": links,
                "headers": headers,
                "date_sent": email_input.date_sent,
                "attachments": email_input.attachments,
                "source": email_input.source or "manual",
                "content_hash": content_hash,
                "split": "predict",  # Default to predict split for dynamic entries
                "created_at": datetime.now(timezone.utc)
            }
            try:
                emails_col.insert_one(new_email)
                logger.info(f"Stored new email document with email_id: {email_id}")
            except DuplicateKeyError:
                # Fallback check in case of race condition writes
                email_record = emails_col.find_one({"content_hash": content_hash})
                if email_record:
                    email_id = email_record["email_id"]
                else:
                    raise RuntimeError("Failed to resolve unique content hash collision on email storage.")
        
        # 2. ML Prediction Inference
        engine = model_service.load_engine()
        
        # Make dict format expected by FeatureExtractor
        email_dict = {
            "subject": subject,
            "body_text": body,
            "sender": sender,
            "links": links,
            "headers": headers,
            "date_sent": email_input.date_sent,
            "attachments": email_input.attachments,
            "source": email_input.source
        }
        
        pred_results = engine.predict(email_dict)
        
        # Run explainability metrics
        explain_results = engine.explain_prediction(email_dict)
        
        # Inspect URL reputations
        from app.services.threat_intel import threat_intel
        intel_report = threat_intel.inspect_urls(links)
        
        # Override ML Prediction for Threat Intel
        if intel_report.get("is_malicious"):
            pred_results["prediction_label"] = "suspicious"
            pred_results["risk_level"] = "high"
            pred_results["confidence"] = max(pred_results["confidence"], 0.95)
        else:
            # Sender Verification Pipeline (Whitelist)
            # Only whitelist if SPF or DKIM passes to prevent spoofing
            spf_pass = headers.get("spf", "").lower() == "pass"
            dkim_pass = headers.get("dkim", "").lower() == "pass"
            
            # If no auth headers exist in the payload (common with basic IMAP extraction),
            # we will still whitelist for MVP, but strongly prefer SPF/DKIM
            no_auth_provided = not headers.get("spf") and not headers.get("dkim")
            
            if spf_pass or dkim_pass or no_auth_provided:
                if sender_domain in TRUSTED_DOMAINS or any(sender_domain.endswith(f".{td}") for td in TRUSTED_DOMAINS):
                    pred_results["prediction_label"] = "legitimate"
                    pred_results["risk_level"] = "low"
                    pred_results["confidence"] = 0.05
                    logger.info(f"Whitelisted sender {sender_domain} as legitimate.")
        
        prediction_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        prediction_doc = {
            "prediction_id": prediction_id,
            "email_id": email_id,
            "model_version": model_service._cached_version,
            "prediction_label": pred_results["prediction_label"],
            "confidence": pred_results["confidence"],
            "risk_level": pred_results["risk_level"],
            "explainability": explain_results,
            "threat_intel": intel_report,
            "user_id": user_id,
            "created_at": now
        }
        
        predictions_col = get_collection("predictions")
        predictions_col.insert_one(prediction_doc)
        logger.info(f"Logged prediction entry {prediction_id} for user {user_id}")
        
        return prediction_doc

    def get_user_history(
        self,
        user_id: str,
        limit: int = 10,
        skip: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        label: Optional[str] = None,
        risk_level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetches user's prediction history, joining and embedding email details.
        """
        predictions_col = get_collection("predictions")
        
        # 1. Match prediction filters
        match_stage = {"user_id": user_id}
        
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            match_stage["created_at"] = date_filter
            
        if label:
            match_stage["prediction_label"] = label
            
        if risk_level:
            match_stage["risk_level"] = risk_level
            
        # MongoDB aggregation pipeline to join collections
        pipeline = [
            {"$match": match_stage},
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "emails",
                    "localField": "email_id",
                    "foreignField": "email_id",
                    "as": "email_info"
                }
            }
        ]
        
        results = list(predictions_col.aggregate(pipeline))
        
        # Flatten email details
        for doc in results:
            # Cast ObjectId if present
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            
            email_info = doc.pop("email_info", [])
            if email_info:
                email_doc = email_info[0]
                if "_id" in email_doc:
                    email_doc["_id"] = str(email_doc["_id"])
                # Map body_text to body to keep response format aligned with EmailInput if desired
                email_doc["body"] = email_doc.get("body_text", "")
                doc["email"] = email_doc
            else:
                doc["email"] = None
                
        return results

# Singleton Instance
prediction_service = PredictionServiceClass()
