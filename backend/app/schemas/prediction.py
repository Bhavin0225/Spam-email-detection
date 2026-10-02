from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    """
    Schema representing the classification response from the prediction engine.
    """
    prediction_id: str = Field(..., description="Unique identifier of this prediction scan")
    email_id: str = Field(..., description="Reference to the stored email ID in the database")
    prediction_label: str = Field(..., description="Classification result ('suspicious' or 'legitimate')")
    confidence: float = Field(..., description="XGBoost model posterior spam class probability")
    risk_level: str = Field(..., description="Derived threat level: 'high', 'medium', or 'low'")
    model_version: str = Field(..., description="Version of the model that executed inference")
    created_at: datetime = Field(..., description="Timestamp of the scan request")
    explainability: Optional[dict] = Field(None, description="Explainability factors")
    threat_intel: Optional[dict] = Field(None, description="Threat intelligence report")

