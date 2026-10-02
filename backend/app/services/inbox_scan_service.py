"""
Orchestration service for batch inbox scanning.
Integrates Google OAuth token management (with encryption) and Gmail/IMAP scanning workflows.
"""

import base64
import hashlib
import time
import uuid
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from cryptography.fernet import Fernet
from app.config import settings
from app.database.collections import get_collection
from app.utils.logger import logger
from app.services.email_providers import gmail_connector, imap_connector
from app.services.prediction_service import prediction_service
from app.schemas.email import EmailInput
from app.schemas.inbox import (
    ScanReport,
    ScanResultItem,
    GmailConnectionStatus,
    ScanHistoryItem
)


def _get_encryption_cipher() -> Fernet:
    """Derive a 32-byte Fernet-compatible key deterministically from settings.JWT_SECRET_KEY."""
    key_hash = hashlib.sha256(settings.JWT_SECRET_KEY.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key_hash)
    return Fernet(fernet_key)


def encrypt_token(token: str) -> str:
    """Encrypt a sensitive token string."""
    if not token:
        return ""
    cipher = _get_encryption_cipher()
    return cipher.encrypt(token.encode()).decode("utf-8")


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt an encrypted token string."""
    if not encrypted_token:
        return ""
    cipher = _get_encryption_cipher()
    return cipher.decrypt(encrypted_token.encode()).decode("utf-8")


class InboxScanServiceClass:
    """
    Orchestrates batch scan triggers, credential encryption/decryption,
    token refreshing, and scan session logging.
    """

    def get_gmail_status(self, user_id: str) -> GmailConnectionStatus:
        """Checks if the user has an active Gmail OAuth2 connection."""
        tokens_col = get_collection("user_oauth_tokens")
        token_doc = tokens_col.find_one({"user_id": user_id, "provider": "gmail"})
        
        if not token_doc:
            return GmailConnectionStatus(connected=False)
            
        return GmailConnectionStatus(
            connected=True,
            email=token_doc.get("email"),
            connected_at=token_doc.get("connected_at")
        )

    def disconnect_gmail(self, user_id: str) -> bool:
        """Removes Gmail OAuth2 tokens for a user."""
        tokens_col = get_collection("user_oauth_tokens")
        res = tokens_col.delete_one({"user_id": user_id, "provider": "gmail"})
        return res.deleted_count > 0

    def save_gmail_tokens(self, user_id: str, token_data: dict) -> str:
        """
        Encrypts and stores Gmail OAuth credentials for a user.
        Queries Gmail API to fetch the user's email address for display.
        """
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in", 3600)
        
        # Calculate expires_at
        expires_at = datetime.fromtimestamp(time.time() + expires_in, tz=timezone.utc)
        
        # Call profile API to fetch email address
        email_address = "Connected Gmail Account"
        try:
            profile_res = requests.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/profile",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=20
            )
            if profile_res.status_code == 200:
                email_address = profile_res.json().get("emailAddress", email_address)
        except Exception as e:
            logger.warning(f"Could not retrieve Gmail user profile: {str(e)}")

        tokens_col = get_collection("user_oauth_tokens")
        
        encrypted_access = encrypt_token(access_token)
        update_doc: Dict[str, Any] = {
            "access_token": encrypted_access,
            "expires_at": expires_at,
            "email": email_address,
            "connected_at": datetime.now(timezone.utc)
        }
        
        # Only overwrite refresh token if it is provided (Google doesn't send it on repeat consents unless prompt=consent is used)
        if refresh_token:
            update_doc["refresh_token"] = encrypt_token(refresh_token)
            
        tokens_col.update_one(
            {"user_id": user_id, "provider": "gmail"},
            {"$set": update_doc},
            upsert=True
        )
        logger.info(f"Stored encrypted Gmail tokens for user {user_id} ({email_address})")
        return email_address

    def _get_valid_gmail_token(self, user_id: str) -> str:
        """Retrieves and, if necessary, refreshes a user's Gmail access token."""
        tokens_col = get_collection("user_oauth_tokens")
        token_doc = tokens_col.find_one({"user_id": user_id, "provider": "gmail"})
        
        if not token_doc:
            raise ValueError("Gmail accounts is not connected.")
            
        expires_at = token_doc.get("expires_at")
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
            
        access_token = decrypt_token(token_doc.get("access_token"))
        
        # Check if token is expired or expiring in less than 30 seconds
        if expires_at.timestamp() < time.time() + 30:
            logger.info(f"Gmail access token for user {user_id} is expired or expiring soon. Refreshing...")
            encrypted_refresh = token_doc.get("refresh_token")
            if not encrypted_refresh:
                raise ValueError("Gmail connection expired and refresh token is missing. Please reconnect.")
                
            refresh_token = decrypt_token(encrypted_refresh)
            try:
                refresh_data = gmail_connector.refresh_access_token(refresh_token)
                new_access = refresh_data.get("access_token")
                expires_in = refresh_data.get("expires_in", 3600)
                
                # Update DB with new token
                new_expires_at = datetime.fromtimestamp(time.time() + expires_in, tz=timezone.utc)
                tokens_col.update_one(
                    {"user_id": user_id, "provider": "gmail"},
                    {"$set": {
                        "access_token": encrypt_token(new_access),
                        "expires_at": new_expires_at
                    }}
                )
                logger.info(f"Successfully refreshed and saved Gmail access token for user {user_id}")
                return new_access
            except Exception as e:
                logger.error(f"Failed to refresh Gmail token for user {user_id}: {str(e)}")
                raise ValueError("Failed to refresh Gmail connection. Please reconnect.")
                
        return access_token

    def start_gmail_scan(self, user_id: str, limit: int = 100) -> ScanReport:
        """Fetches last N emails from connected Gmail and performs batch spam classification."""
        start_time = time.time()
        
        # 1. Get access token
        access_token = self._get_valid_gmail_token(user_id)
        
        # 2. Fetch emails
        emails = gmail_connector.fetch_emails(access_token, limit=limit)
        
        # 3. Classify and store predictions
        report = self._process_batch_scan(user_id, "gmail", emails, start_time)
        return report

    def start_imap_scan(self, user_id: str, imap_config: dict, limit: int = 100) -> ScanReport:
        """Fetches last N emails from IMAP account and performs batch spam classification."""
        start_time = time.time()
        
        # 1. Fetch emails
        emails = imap_connector.fetch_emails(
            host=imap_config.get("host", ""),
            port=imap_config.get("port", 993),
            email_address=imap_config.get("email", ""),
            password=imap_config.get("password", ""),
            folder=imap_config.get("folder", "INBOX"),
            limit=limit,
            provider=imap_config.get("provider")
        )
        
        # 2. Classify and store predictions
        report = self._process_batch_scan(user_id, "imap", emails, start_time)
        return report

    def _process_batch_scan(self, user_id: str, provider: str, emails: list, start_time: float) -> ScanReport:
        """Runs a list of parsed email dicts through the spam engine and logs metadata."""
        scan_id = str(uuid.uuid4())
        results = []
        
        spam_count = 0
        legitimate_count = 0
        high_risk_count = 0
        
        for email in emails:
            # Map input to EmailInput schema
            email_input = EmailInput(
                subject=email["subject"],
                body=email["body"],
                sender=email["sender"],
                headers=email["headers"],
                date_sent=email["date_sent"],
                attachments=email["attachments"],
                source=provider
            )
            
            try:
                # Classify & Log individual prediction
                pred_doc = prediction_service.predict_and_store(email_input, user_id)
                
                label = pred_doc["prediction_label"]
                risk = pred_doc["risk_level"]
                
                if label == "suspicious":
                    spam_count += 1
                else:
                    legitimate_count += 1
                    
                if risk == "high":
                    high_risk_count += 1
                    
                results.append(
                    ScanResultItem(
                        subject=email["subject"],
                        sender=email["sender"],
                        prediction_label=label,
                        confidence=pred_doc["confidence"],
                        risk_level=risk,
                        prediction_id=pred_doc["prediction_id"],
                        date_sent=email["date_sent"],
                        has_attachments=len(email["attachments"]) > 0
                    )
                )
            except Exception as e:
                logger.error(f"Error classifying email in batch scan {scan_id}: {str(e)}")
                continue
                
        duration = round(time.time() - start_time, 2)
        created_at = datetime.now(timezone.utc)
        
        # Store scan history document in MongoDB
        scan_doc = {
            "scan_id": scan_id,
            "user_id": user_id,
            "provider": provider,
            "total_scanned": len(results),
            "spam_count": spam_count,
            "legitimate_count": legitimate_count,
            "high_risk_count": high_risk_count,
            "scan_duration_seconds": duration,
            "created_at": created_at
        }
        
        get_collection("inbox_scans").insert_one(scan_doc)
        logger.info(f"Saved inbox scan session {scan_id} ({provider}) for user {user_id}. Scanned {len(results)} emails.")
        
        return ScanReport(
            scan_id=scan_id,
            provider=provider,
            total_scanned=len(results),
            spam_count=spam_count,
            legitimate_count=legitimate_count,
            high_risk_count=high_risk_count,
            scan_duration_seconds=duration,
            results=results,
            created_at=created_at
        )

    def get_user_scan_history(self, user_id: str, limit: int = 10, skip: int = 0) -> List[ScanHistoryItem]:
        """Fetches history of past scan sessions for a user."""
        scans_col = get_collection("inbox_scans")
        cursor = scans_col.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
        
        history = []
        for doc in cursor:
            history.append(
                ScanHistoryItem(
                    scan_id=doc["scan_id"],
                    provider=doc["provider"],
                    total_scanned=doc["total_scanned"],
                    spam_count=doc["spam_count"],
                    legitimate_count=doc["legitimate_count"],
                    high_risk_count=doc["high_risk_count"],
                    scan_duration_seconds=doc["scan_duration_seconds"],
                    created_at=doc["created_at"]
                )
            )
        return history


# Singleton instance
inbox_scan_service = InboxScanServiceClass()
