from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class EmailInput(BaseModel):
    """
    Schema for new email predict requests.
    """
    subject: str = Field(..., description="The subject line of the email")
    body: str = Field(..., description="The main body text of the email")
    sender: str = Field(..., description="The sender's email address or name")
    headers: Optional[dict] = Field(None, description="Optional email security and routing headers")
    date_sent: Optional[datetime] = Field(None, description="Original email send date")
    attachments: Optional[List[dict]] = Field(None, description="List of attachments metadata")
    source: Optional[str] = Field("manual", description="Source of the email (manual, gmail, imap)")

