"""
Gmail API connector using OAuth2 for inbox scanning.
Handles: OAuth URL generation, token exchange, email fetching via Gmail API.
"""

import base64
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.config import settings
from app.utils.logger import logger


def get_auth_url(redirect_uri: Optional[str] = None) -> str:
    """
    Generates a Google OAuth2 consent URL with gmail.readonly scope.
    Returns the URL for the frontend to redirect the user to.
    """
    client_id = settings.GOOGLE_CLIENT_ID
    redirect = redirect_uri or settings.GOOGLE_REDIRECT_URI
    scope = "https://www.googleapis.com/auth/gmail.readonly"
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect}"
        f"&response_type=code"
        f"&scope={scope}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return auth_url


def exchange_code(code: str, redirect_uri: Optional[str] = None) -> dict:
    """
    Exchanges an authorization code for access and refresh tokens.
    Returns dict with: access_token, refresh_token, expires_in, token_type.
    """
    import requests

    token_url = "https://oauth2.googleapis.com/token"
    redirect = redirect_uri or settings.GOOGLE_REDIRECT_URI

    payload = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect,
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, data=payload, timeout=30)
    
    if response.status_code != 200:
        logger.error(f"Gmail token exchange failed: {response.status_code} - {response.text}")
        raise ValueError(f"Failed to exchange authorization code: {response.text}")

    token_data = response.json()
    logger.info("Successfully exchanged Gmail OAuth authorization code for tokens.")
    return token_data


def refresh_access_token(refresh_token: str) -> dict:
    """
    Uses a refresh token to get a new access token.
    """
    import requests

    token_url = "https://oauth2.googleapis.com/token"

    payload = {
        "refresh_token": refresh_token,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "grant_type": "refresh_token",
    }

    response = requests.post(token_url, data=payload, timeout=30)

    if response.status_code != 200:
        logger.error(f"Gmail token refresh failed: {response.status_code}")
        raise ValueError("Failed to refresh Gmail access token.")

    return response.json()


def _parse_gmail_message(msg_payload: dict) -> Dict[str, Any]:
    """
    Parses a Gmail API message payload into a structured email dict.
    Extracts: subject, body, sender, reply-to, date, headers, attachments.
    """
    headers_list = msg_payload.get("payload", {}).get("headers", [])
    
    # Build headers lookup
    headers_map = {}
    for h in headers_list:
        headers_map[h["name"].lower()] = h["value"]
    
    subject = headers_map.get("subject", "(No Subject)")
    sender = headers_map.get("from", "")
    reply_to = headers_map.get("reply-to", "")
    date_str = headers_map.get("date", "")
    
    # Parse authentication results for SPF/DKIM/DMARC
    auth_results = headers_map.get("authentication-results", "")
    spf = "pass" if "spf=pass" in auth_results.lower() else ("fail" if "spf=fail" in auth_results.lower() else "")
    dkim = "pass" if "dkim=pass" in auth_results.lower() else ("fail" if "dkim=fail" in auth_results.lower() else "")
    dmarc = "pass" if "dmarc=pass" in auth_results.lower() else ("fail" if "dmarc=fail" in auth_results.lower() else "")
    
    # Count hops from Received headers
    hop_count = sum(1 for h in headers_list if h["name"].lower() == "received")
    
    # Extract body text (prefer text/plain, fallback to text/html)
    body = _extract_body(msg_payload.get("payload", {}))
    
    # Extract attachment metadata
    attachments = _extract_attachments(msg_payload.get("payload", {}))
    
    # Parse internal date (epoch ms)
    internal_date_ms = int(msg_payload.get("internalDate", "0"))
    date_sent = datetime.fromtimestamp(internal_date_ms / 1000, tz=timezone.utc) if internal_date_ms else None
    
    return {
        "subject": subject,
        "body": body,
        "sender": sender,
        "headers": {
            "spf": spf,
            "dkim": dkim,
            "dmarc": dmarc,
            "reply-to": reply_to,
            "hop_count": hop_count,
        },
        "date_sent": date_sent,
        "attachments": attachments,
        "source": "gmail",
        "gmail_message_id": msg_payload.get("id", ""),
    }


def _extract_body(payload: dict) -> str:
    """
    Recursively extracts the email body text from Gmail MIME payload.
    Prefers text/plain; falls back to text/html.
    """
    mime_type = payload.get("mimeType", "")
    
    # Direct body data
    if mime_type == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    
    if mime_type == "text/html":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    
    # Multipart — recurse into parts
    parts = payload.get("parts", [])
    text_body = ""
    html_body = ""
    
    for part in parts:
        part_mime = part.get("mimeType", "")
        if part_mime == "text/plain":
            data = part.get("body", {}).get("data", "")
            if data:
                text_body = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        elif part_mime == "text/html":
            data = part.get("body", {}).get("data", "")
            if data:
                html_body = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        elif "multipart" in part_mime:
            # Recurse into nested multipart
            nested = _extract_body(part)
            if nested:
                text_body = text_body or nested
    
    return text_body or html_body or ""


def _extract_attachments(payload: dict) -> List[Dict[str, str]]:
    """
    Extracts attachment metadata (filename, content_type) from Gmail payload.
    """
    attachments = []
    parts = payload.get("parts", [])
    
    for part in parts:
        filename = part.get("filename", "")
        if filename:
            attachments.append({
                "filename": filename,
                "content_type": part.get("mimeType", "unknown"),
            })
        # Recurse into nested parts
        nested_parts = part.get("parts", [])
        for nested in nested_parts:
            nested_filename = nested.get("filename", "")
            if nested_filename:
                attachments.append({
                    "filename": nested_filename,
                    "content_type": nested.get("mimeType", "unknown"),
                })
    
    return attachments


def fetch_emails(access_token: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Fetches the last N emails from a Gmail inbox using the Gmail API.
    Uses messages.list to get message IDs, then messages.get for full payloads.
    
    Returns a list of parsed email dicts ready for the prediction pipeline.
    """
    import requests
    
    base_url = "https://gmail.googleapis.com/gmail/v1/users/me"
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    
    # Step 1: List message IDs
    message_ids = []
    next_page_token = None
    
    while len(message_ids) < limit:
        params = {"maxResults": min(limit - len(message_ids), 100)}
        if next_page_token:
            params["pageToken"] = next_page_token
        
        response = requests.get(
            f"{base_url}/messages",
            headers=auth_headers,
            params=params,
            timeout=30,
        )
        
        if response.status_code == 401:
            raise ValueError("Gmail access token expired or invalid.")
        if response.status_code != 200:
            logger.error(f"Gmail messages.list failed: {response.status_code}")
            raise ValueError(f"Failed to list Gmail messages: {response.text}")
        
        data = response.json()
        messages = data.get("messages", [])
        
        if not messages:
            break
        
        message_ids.extend([m["id"] for m in messages])
        next_page_token = data.get("nextPageToken")
        
        if not next_page_token:
            break
    
    # Step 2: Fetch full message payloads
    emails = []
    for msg_id in message_ids[:limit]:
        try:
            response = requests.get(
                f"{base_url}/messages/{msg_id}",
                headers=auth_headers,
                params={"format": "full"},
                timeout=30,
            )
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch Gmail message {msg_id}: {response.status_code}")
                continue
            
            msg_data = response.json()
            parsed = _parse_gmail_message(msg_data)
            emails.append(parsed)
            
        except Exception as e:
            logger.warning(f"Error parsing Gmail message {msg_id}: {str(e)}")
            continue
    
    logger.info(f"Successfully fetched {len(emails)} emails from Gmail inbox.")
    return emails
