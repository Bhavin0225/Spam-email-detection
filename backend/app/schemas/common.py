from typing import Optional
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    """
    Response schema for the system health check API.
    """
    status: str = Field(..., description="API server status, typically 'ok'")
    database: str = Field(..., description="Database connection status, typically 'connected'")
    model: Optional[str] = Field(None, description="ML model state, loaded or not")
    version: Optional[str] = Field(None, description="Active machine learning model version")

class ErrorResponse(BaseModel):
    """
    Standard schema for returning errors to clients.
    """
    detail: str = Field(..., description="Error detail message")
