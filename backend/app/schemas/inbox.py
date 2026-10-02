"""
Pydantic schemas for inbox scanning requests and responses.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class GmailAuthCallbackRequest(BaseModel):
    """Request body for exchanging Gmail OAuth authorization code."""
    code: str = Field(..., description="OAuth2 authorization code from Google callback")
    redirect_uri: Optional[str] = Field(None, description="Custom redirect URI (optional)")


class GmailScanRequest(BaseModel):
    """Request to trigger a Gmail inbox scan."""
    limit: int = Field(100, ge=1, le=200, description="Number of emails to fetch and scan")


class ImapScanRequest(BaseModel):
    """Request to trigger an IMAP inbox scan."""
    host: str = Field(..., description="IMAP server hostname")
    port: int = Field(993, ge=1, le=65535, description="IMAP server port")
    email: str = Field(..., description="Email address for IMAP login")
    password: str = Field(..., description="App password for IMAP authentication")
    folder: str = Field("INBOX", description="Mailbox folder to scan")
    limit: int = Field(100, ge=1, le=200, description="Number of emails to fetch and scan")
    provider: Optional[str] = Field(None, description="Provider shortcut: 'gmail', 'outlook', 'yahoo'")


class ScanResultItem(BaseModel):
    """Individual email scan result within a batch report."""
    subject: str = Field("", description="Email subject line")
    sender: str = Field("", description="Sender email address")
    prediction_label: str = Field(..., description="Classification: 'suspicious' or 'legitimate'")
    confidence: float = Field(..., description="Model confidence score")
    risk_level: str = Field(..., description="Threat level: 'high', 'medium', or 'low'")
    prediction_id: str = Field(..., description="Unique prediction ID for this scan")
    date_sent: Optional[datetime] = Field(None, description="Original email send date")
    has_attachments: bool = Field(False, description="Whether the email has attachments")


class ScanReport(BaseModel):
    """Aggregated batch scan report returned after inbox scanning."""
    scan_id: str = Field(..., description="Unique scan session identifier")
    provider: str = Field(..., description="Email provider: 'gmail' or 'imap'")
    total_scanned: int = Field(..., description="Total emails successfully scanned")
    spam_count: int = Field(..., description="Number flagged as suspicious")
    legitimate_count: int = Field(..., description="Number classified as legitimate")
    high_risk_count: int = Field(..., description="Number with high risk level")
    scan_duration_seconds: float = Field(..., description="Total scan processing time")
    results: List[ScanResultItem] = Field(default_factory=list, description="Individual scan results")
    created_at: datetime = Field(..., description="Scan session timestamp")


class GmailConnectionStatus(BaseModel):
    """Status of a user's Gmail OAuth connection."""
    connected: bool = Field(..., description="Whether Gmail is connected")
    email: Optional[str] = Field(None, description="Connected Gmail address")
    connected_at: Optional[datetime] = Field(None, description="When the connection was established")


class ScanHistoryItem(BaseModel):
    """Summary of a past scan session."""
    scan_id: str
    provider: str
    total_scanned: int
    spam_count: int
    legitimate_count: int
    high_risk_count: int
    scan_duration_seconds: float
    created_at: datetime
