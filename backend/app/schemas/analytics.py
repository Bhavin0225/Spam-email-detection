from typing import List, Dict, Any
from pydantic import BaseModel, Field

class AnalyticsResponse(BaseModel):
    """
    Schema containing statistical summaries of prediction activity and accuracy.
    """
    total_scans: int = Field(..., description="Total count of email scans conducted")
    spam_rate: float = Field(..., description="Fraction of scans flagged as suspicious")
    false_positive_rate: float = Field(..., description="Rate of legitimate emails marked as suspicious based on user feedback")
    predictions_over_time: List[Dict[str, Any]] = Field(
        ..., description="Daily counts of scans, spam classification ratios, and volumes"
    )
    top_suspicious_domains: List[Dict[str, Any]] = Field(
        ..., description="Top sender domains flagged for spam/suspicious outputs"
    )
