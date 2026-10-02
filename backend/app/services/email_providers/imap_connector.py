"""
Universal IMAP connector for inbox scanning.
Supports Gmail, Outlook, Yahoo, and any custom IMAP server.
"""

import imaplib
import email
import re
from email import policy
from email.header import decode_header
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.services.email_providers import IMAP_PROVIDERS
from app.utils.logger import logger


def _decode_header_value(value: str) -> str:
    """Decode an email header value that may be encoded (e.g., RFC 2047)."""
    if not value:
        return ""
    decoded_parts = decode_header(value)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(str(part))
    return " ".join(result)


def _parse_imap_message(raw_bytes: bytes) -> Dict[str, Any]:
    """
    Parses raw IMAP message bytes into a structured email dict.
    Uses Python's email.message_from_bytes for MIME parsing.
    """
    msg = email.message_from_bytes(raw_bytes, policy=policy.default)
    
    # Extract headers
    subject = _decode_header_value(msg.get("Subject", "(No Subject)"))
    sender = _decode_header_value(msg.get("From", ""))
    reply_to = _decode_header_value(msg.get("Reply-To", ""))
    date_str = msg.get("Date", "")
    
    # Parse Authentication-Results header
    auth_results = msg.get("Authentication-Results", "")
    spf = "pass" if "spf=pass" in auth_results.lower() else ("fail" if "spf=fail" in auth_results.lower() else "")
    dkim = "pass" if "dkim=pass" in auth_results.lower() else ("fail" if "dkim=fail" in auth_results.lower() else "")
    dmarc = "pass" if "dmarc=pass" in auth_results.lower() else ("fail" if "dmarc=fail" in auth_results.lower() else "")
    
    # Count Received headers for hop count
    hop_count = len(msg.get_all("Received", []))
    
    # Extract body text
    body = ""
    html_body = ""
    attachments = []
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            
            # Check for attachments
            if "attachment" in content_disposition or part.get_filename():
                filename = part.get_filename() or ""
                if filename:
                    attachments.append({
                        "filename": filename,
                        "content_type": content_type,
                    })
                continue
            
            if content_type == "text/plain" and not body:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    body = payload.decode(charset, errors="replace")
            elif content_type == "text/html" and not html_body:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    html_body = payload.decode(charset, errors="replace")
    else:
        content_type = msg.get_content_type()
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            text = payload.decode(charset, errors="replace")
            if content_type == "text/plain":
                body = text
            else:
                html_body = text
    
    # Prefer plain text, fall back to HTML
    final_body = body or html_body or ""
    
    # Parse date
    date_sent = None
    if date_str:
        try:
            date_sent = email.utils.parsedate_to_datetime(date_str)
            if date_sent.tzinfo is None:
                date_sent = date_sent.replace(tzinfo=timezone.utc)
        except Exception:
            date_sent = None
    
    return {
        "subject": subject,
        "body": final_body,
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
        "source": "imap",
    }


def fetch_emails(
    host: str,
    port: int,
    email_address: str,
    password: str,
    folder: str = "INBOX",
    limit: int = 100,
    use_ssl: bool = True,
    provider: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Connects to an IMAP server and fetches the last N emails.
    
    Supports pre-configured providers (gmail, outlook, yahoo) via the provider param,
    or custom IMAP servers via explicit host/port.
    
    Args:
        host: IMAP server hostname.
        port: IMAP server port.
        email_address: User's email address for login.
        password: App password (NOT the main password for providers with 2FA).
        folder: Mailbox folder to scan (default INBOX).
        limit: Maximum number of emails to fetch.
        use_ssl: Whether to use SSL (default True).
        provider: Optional provider key ('gmail', 'outlook', 'yahoo') to auto-resolve host/port.
    
    Returns:
        List of parsed email dicts.
    """
    # Resolve provider presets
    if provider and provider.lower() in IMAP_PROVIDERS:
        preset = IMAP_PROVIDERS[provider.lower()]
        host = preset["host"]
        port = preset["port"]
    
    logger.info(f"Connecting to IMAP server {host}:{port} for {email_address}...")
    
    try:
        if use_ssl:
            mail = imaplib.IMAP4_SSL(host, port, timeout=30)
        else:
            mail = imaplib.IMAP4(host, port, timeout=30)
        
        # Google App Passwords are often pasted with spaces (e.g., 'abcd efgh ijkl mnop')
        # We must strip them to avoid authentication errors
        clean_password = password.replace(" ", "")
        mail.login(email_address, clean_password)
        logger.info(f"Successfully authenticated with IMAP server as {email_address}.")
    except imaplib.IMAP4.error as e:
        logger.error(f"IMAP authentication failed for {email_address}: {str(e)}")
        raise ValueError(f"IMAP authentication failed: {str(e)}")
    except Exception as e:
        logger.error(f"IMAP connection error: {str(e)}")
        raise ConnectionError(f"Failed to connect to IMAP server {host}:{port}: {str(e)}")
    
    try:
        # Select mailbox folder
        status, folder_data = mail.select(folder, readonly=True)
        if status != "OK":
            raise ValueError(f"Failed to select folder '{folder}': {folder_data}")
        
        # Search for all messages and take the last N
        status, msg_ids = mail.search(None, "ALL")
        if status != "OK" or not msg_ids[0]:
            logger.info(f"No messages found in {folder}.")
            return []
        
        all_ids = msg_ids[0].split()
        # Take the most recent N emails (end of the list)
        target_ids = all_ids[-limit:]
        # Reverse so newest is first
        target_ids.reverse()
        
        emails = []
        for msg_id in target_ids:
            try:
                status, msg_data = mail.fetch(msg_id, "(RFC822)")
                if status != "OK" or not msg_data or not msg_data[0]:
                    continue
                
                raw_bytes = msg_data[0][1]
                if isinstance(raw_bytes, bytes):
                    parsed = _parse_imap_message(raw_bytes)
                    emails.append(parsed)
            except Exception as e:
                logger.warning(f"Error fetching/parsing IMAP message {msg_id}: {str(e)}")
                continue
        
        logger.info(f"Successfully fetched {len(emails)} emails from {email_address} ({folder}).")
        return emails
        
    finally:
        try:
            mail.close()
            mail.logout()
        except Exception:
            pass
