from datetime import datetime, timezone
from app.database.collections import get_collection
from app.utils.logger import logger

class AnalyticsServiceClass:
    """
    Service using MongoDB aggregation pipelines to calculate total scans,
    spam classification rates, false positive rates, scan volumes over time,
    and top suspicious domains.
    """
    def get_system_analytics(self) -> dict:
        """
        Runs aggregation queries across collections and returns structured system analytics.
        """
        predictions_col = get_collection("predictions")
        feedback_col = get_collection("feedback")
        
        # 1. Total Scans
        total_scans = predictions_col.count_documents({})
        
        # 2. Spam Rate
        spam_scans = predictions_col.count_documents({"prediction_label": "suspicious"})
        spam_rate = float(spam_scans / total_scans) if total_scans > 0 else 0.0
        
        # 3. False Positive Rate (FPR) = FP / (FP + TN) on feedbacked predictions
        # Lookup predictions in feedback to compute true labels
        pipeline_feedback = [
            {
                "$lookup": {
                    "from": "predictions",
                    "localField": "prediction_id",
                    "foreignField": "prediction_id",
                    "as": "pred_info"
                }
            },
            {"$unwind": "$pred_info"},
            {
                "$project": {
                    "was_correct": 1,
                    "prediction_label": "$pred_info.prediction_label"
                }
            }
        ]
        
        feedback_items = list(feedback_col.aggregate(pipeline_feedback))
        
        fps = 0
        tns = 0
        for item in feedback_items:
            pred_label = item.get("prediction_label", "")
            was_correct = item.get("was_correct", True)
            
            # False Positive: predicted suspicious but it was actually legitimate (incorrect)
            if pred_label == "suspicious" and not was_correct:
                fps += 1
            # True Negative: predicted legitimate and it was indeed legitimate (correct)
            elif pred_label == "legitimate" and was_correct:
                tns += 1
                
        false_positive_rate = float(fps / (fps + tns)) if (fps + tns) > 0 else 0.0
        
        # 4. Predictions Over Time (grouped by day)
        pipeline_time = [
            {
                "$project": {
                    "day": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "is_spam": {
                        "$cond": [{"$eq": ["$prediction_label", "suspicious"]}, 1, 0]
                    },
                    "is_ham": {
                        "$cond": [{"$eq": ["$prediction_label", "legitimate"]}, 1, 0]
                    }
                }
            },
            {
                "$group": {
                    "_id": "$day",
                    "total": {"$sum": 1},
                    "spam": {"$sum": "$is_spam"},
                    "ham": {"$sum": "$is_ham"}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        time_aggregations = list(predictions_col.aggregate(pipeline_time))
        predictions_over_time = []
        for ta in time_aggregations:
            predictions_over_time.append({
                "date": ta["_id"],
                "total": ta["total"],
                "spam": ta["spam"],
                "ham": ta["ham"]
            })
            
        # 5. Top Suspicious Domains
        pipeline_domains = [
            {"$match": {"prediction_label": "suspicious"}},
            {
                "$lookup": {
                    "from": "emails",
                    "localField": "email_id",
                    "foreignField": "email_id",
                    "as": "email_info"
                }
            },
            {"$unwind": "$email_info"},
            {
                "$group": {
                    "_id": "$email_info.sender_domain",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        
        domain_aggregations = list(predictions_col.aggregate(pipeline_domains))
        top_suspicious_domains = []
        for da in domain_aggregations:
            # Skip empty domain names if they exist
            domain = da["_id"] or "unknown"
            top_suspicious_domains.append({
                "domain": domain,
                "count": da["count"]
            })
            
        return {
            "total_scans": total_scans,
            "spam_rate": spam_rate,
            "false_positive_rate": false_positive_rate,
            "predictions_over_time": predictions_over_time,
            "top_suspicious_domains": top_suspicious_domains
        }

# Singleton Instance
analytics_service = AnalyticsServiceClass()
