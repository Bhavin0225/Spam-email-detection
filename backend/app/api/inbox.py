"""
API endpoints for inbox scanning and authentication callback actions.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from app.core.permissions import require_user
from app.services.email_providers import gmail_connector
from app.services.inbox_scan_service import inbox_scan_service
from app.schemas.inbox import (
    GmailAuthCallbackRequest,
    GmailScanRequest,
    ImapScanRequest,
    ScanReport,
    GmailConnectionStatus,
    ScanHistoryItem
)

router = APIRouter(prefix="/inbox", tags=["Inbox Scanner"])


@router.get("/gmail/auth-url", summary="Get Gmail OAuth Authorization URL")
def get_gmail_auth_url(redirect_uri: Optional[str] = None, current_user: dict = Depends(require_user)):
    """Generates the Google OAuth2 consent URL for the frontend flow."""
    try:
        url = gmail_connector.get_auth_url(redirect_uri)
        return {"auth_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate authorization URL: {str(e)}")


@router.post("/gmail/callback", summary="Gmail OAuth Authorization Callback")
def gmail_callback(body: GmailAuthCallbackRequest, current_user: dict = Depends(require_user)):
    """Receives Gmail authorization code, exchanges it for tokens, and stores them securely."""
    try:
        token_data = gmail_connector.exchange_code(body.code, body.redirect_uri)
        email = inbox_scan_service.save_gmail_tokens(current_user["user_id"], token_data)
        return {"status": "success", "email": email}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete OAuth callback: {str(e)}")


@router.get("/gmail/status", response_model=GmailConnectionStatus, summary="Get Gmail Connection Status")
def get_gmail_status(current_user: dict = Depends(require_user)):
    """Returns the Gmail OAuth connection status for the authenticated user."""
    return inbox_scan_service.get_gmail_status(current_user["user_id"])


@router.delete("/gmail/disconnect", summary="Disconnect Gmail Account")
def disconnect_gmail(current_user: dict = Depends(require_user)):
    """Removes the stored Google OAuth tokens for the authenticated user."""
    disconnected = inbox_scan_service.disconnect_gmail(current_user["user_id"])
    if not disconnected:
        raise HTTPException(status_code=404, detail="Gmail connection not found.")
    return {"status": "success", "message": "Gmail disconnected successfully."}


@router.post("/gmail/scan", response_model=ScanReport, summary="Scan Gmail Inbox")
def scan_gmail_inbox(body: GmailScanRequest, current_user: dict = Depends(require_user)):
    """Triggers an inbox scan on the user's connected Gmail account."""
    try:
        return inbox_scan_service.start_gmail_scan(current_user["user_id"], limit=body.limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gmail scan failed: {str(e)}")


@router.post("/inbox/imap/scan", response_model=ScanReport, summary="Scan IMAP Inbox")
@router.post("/imap/scan", response_model=ScanReport, summary="Scan IMAP Inbox")
def scan_imap_inbox(body: ImapScanRequest, current_user: dict = Depends(require_user)):
    """Triggers a scan on any IMAP-compatible mailbox (credentials are used in-memory only)."""
    try:
        imap_config = {
            "host": body.host,
            "port": body.port,
            "email": body.email,
            "password": body.password,
            "folder": body.folder,
            "provider": body.provider
        }
        return inbox_scan_service.start_imap_scan(current_user["user_id"], imap_config, limit=body.limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IMAP scan failed: {str(e)}")


@router.get("/scans", response_model=List[ScanHistoryItem], summary="Get User Scan History")
def get_scan_history(
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: dict = Depends(require_user)
):
    """Retrieves a paginated list of past inbox scan sessions for the authenticated user."""
    return inbox_scan_service.get_user_scan_history(current_user["user_id"], limit=limit, skip=skip)
