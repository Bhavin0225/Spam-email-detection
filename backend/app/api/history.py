from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from app.core.permissions import require_user
from app.services.prediction_service import prediction_service

router = APIRouter(prefix="/history", tags=["Predictions"])

@router.get(
    "",
    response_model=List[Dict[str, Any]],
    summary="Get Paginated Prediction Scan History",
    description="Returns chronological scans executed by the authenticated user. Supports skipping, page-limiting, and metric-filtering (date ranges, risk bands, labels)."
)
def get_history(
    limit: int = Query(10, ge=1, le=100, description="Maximum count of results per page"),
    skip: int = Query(0, ge=0, description="Offset count of items to skip"),
    start_date: Optional[datetime] = Query(None, description="Start date ISO timestamp filter"),
    end_date: Optional[datetime] = Query(None, description="End date ISO timestamp filter"),
    label: Optional[str] = Query(None, description="Filter results by prediction label ('suspicious' or 'legitimate')"),
    risk_level: Optional[str] = Query(None, description="Filter results by risk band ('high', 'medium', or 'low')"),
    current_user: dict = Depends(require_user)
):
    user_id = current_user["user_id"]
    return prediction_service.get_user_history(
        user_id=user_id,
        limit=limit,
        skip=skip,
        start_date=start_date,
        end_date=end_date,
        label=label,
        risk_level=risk_level
    )

@router.get(
    "/{prediction_id}",
    response_model=Dict[str, Any],
    summary="Get Specific Prediction History Record",
    description="Returns a single prediction record by ID."
)
def get_prediction(prediction_id: str, current_user: dict = Depends(require_user)):
    from app.database.collections import get_collection
    from fastapi import HTTPException
    
    user_id = current_user["user_id"]
    predictions_col = get_collection("predictions")
    doc = predictions_col.find_one({"prediction_id": prediction_id, "user_id": user_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Prediction record not found.")
        
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
        
    emails_col = get_collection("emails")
    email_doc = emails_col.find_one({"email_id": doc["email_id"]})
    if email_doc:
        if "_id" in email_doc:
            email_doc["_id"] = str(email_doc["_id"])
        email_doc["body"] = email_doc.get("body_text", "")
        doc["email"] = email_doc
    else:
        doc["email"] = None
        
    return doc
