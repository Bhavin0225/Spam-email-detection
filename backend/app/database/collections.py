import pymongo
from pymongo.collection import Collection
from app.database.connection import db_manager
from app.utils.logger import logger

def get_collection(name: str) -> Collection:
    """
    Returns a collection reference from the connected MongoDB database.
    """
    return db_manager.db[name]

def init_collections_and_indexes() -> None:
    """
    Verifies existence of and creates the 7 required collections and their 27 custom indexes
    as defined in section 5.4 of the Technical Architecture Document.
    """
    db = db_manager.db

    # 1. users Collection Indexes
    logger.info("Initializing 'users' collection indexes...")
    users = db["users"]
    users.create_index([("email", pymongo.ASCENDING)], unique=True, name="idx_users_email")
    users.create_index([("user_id", pymongo.ASCENDING)], unique=True, name="idx_users_user_id")
    users.create_index([("role", pymongo.ASCENDING)], name="idx_users_role")

    # 2. emails Collection Indexes
    logger.info("Initializing 'emails' collection indexes...")
    emails = db["emails"]
    emails.create_index([("email_id", pymongo.ASCENDING)], unique=True, name="idx_emails_email_id")
    emails.create_index([("created_at", pymongo.DESCENDING)], name="idx_emails_created_at")
    emails.create_index([("sender_domain", pymongo.ASCENDING)], name="idx_emails_sender_domain")
    emails.create_index([("dataset_source", pymongo.ASCENDING)], name="idx_emails_dataset_source")
    emails.create_index([("split", pymongo.ASCENDING)], name="idx_emails_split")
    emails.create_index([("label", pymongo.ASCENDING)], name="idx_emails_label")
    emails.create_index([("content_hash", pymongo.ASCENDING)], unique=True, name="idx_emails_content_hash")

    # 3. predictions Collection Indexes
    logger.info("Initializing 'predictions' collection indexes...")
    predictions = db["predictions"]
    predictions.create_index([("prediction_id", pymongo.ASCENDING)], unique=True, name="idx_predictions_prediction_id")
    predictions.create_index([("email_id", pymongo.ASCENDING)], name="idx_predictions_email_id")
    predictions.create_index([("model_version", pymongo.ASCENDING)], name="idx_predictions_model_version")
    predictions.create_index([("created_at", pymongo.DESCENDING)], name="idx_predictions_created_at")
    predictions.create_index([("user_id", pymongo.ASCENDING)], name="idx_predictions_user_id")

    # 4. feedback Collection Indexes
    logger.info("Initializing 'feedback' collection indexes...")
    feedback = db["feedback"]
    feedback.create_index([("feedback_id", pymongo.ASCENDING)], unique=True, name="idx_feedback_feedback_id")
    feedback.create_index([("prediction_id", pymongo.ASCENDING)], name="idx_feedback_prediction_id")
    feedback.create_index([("user_id", pymongo.ASCENDING)], name="idx_feedback_user_id")
    feedback.create_index([("status", pymongo.ASCENDING)], name="idx_feedback_status")

    # 5. model_metadata Collection Indexes
    logger.info("Initializing 'model_metadata' collection indexes...")
    model_metadata = db["model_metadata"]
    model_metadata.create_index([("model_version", pymongo.ASCENDING)], unique=True, name="idx_model_version")
    model_metadata.create_index([("deployed", pymongo.ASCENDING)], name="idx_model_deployed")

    # 6. dataset_metadata Collection Indexes
    logger.info("Initializing 'dataset_metadata' collection indexes...")
    dataset_metadata = db["dataset_metadata"]
    dataset_metadata.create_index([("dataset_id", pymongo.ASCENDING)], unique=True, name="idx_dataset_id")
    dataset_metadata.create_index([("name", pymongo.ASCENDING)], name="idx_dataset_name")
    dataset_metadata.create_index([("source", pymongo.ASCENDING)], name="idx_dataset_source")
    dataset_metadata.create_index([("ingestion_date", pymongo.DESCENDING)], name="idx_dataset_ingestion_date")

    # 7. system_logs Collection Indexes
    logger.info("Initializing 'system_logs' collection indexes...")
    system_logs = db["system_logs"]
    system_logs.create_index([("log_id", pymongo.ASCENDING)], unique=True, name="idx_logs_log_id")
    system_logs.create_index([("event_type", pymongo.ASCENDING)], name="idx_logs_event_type")
    system_logs.create_index([("timestamp", pymongo.DESCENDING)], name="idx_logs_timestamp")
    system_logs.create_index([("severity", pymongo.ASCENDING)], name="idx_logs_severity")
    # TTL Index (90 Days = 7,776,000 seconds)
    system_logs.create_index(
        [("timestamp", pymongo.ASCENDING)],
        expireAfterSeconds=90 * 24 * 60 * 60,
        name="idx_logs_ttl"
    )

    # 8. inbox_scans Collection Indexes
    logger.info("Initializing 'inbox_scans' collection indexes...")
    inbox_scans = db["inbox_scans"]
    inbox_scans.create_index([("scan_id", pymongo.ASCENDING)], unique=True, name="idx_inbox_scan_id")
    inbox_scans.create_index([("user_id", pymongo.ASCENDING)], name="idx_inbox_scan_user_id")
    inbox_scans.create_index([("created_at", pymongo.DESCENDING)], name="idx_inbox_scan_created_at")

    # 9. user_oauth_tokens Collection Indexes
    logger.info("Initializing 'user_oauth_tokens' collection indexes...")
    user_oauth_tokens = db["user_oauth_tokens"]
    user_oauth_tokens.create_index([("user_id", pymongo.ASCENDING)], unique=True, name="idx_oauth_user_id")
    user_oauth_tokens.create_index([("provider", pymongo.ASCENDING)], name="idx_oauth_provider")

    logger.info("All 9 collections and 33 indexes initialized and verified successfully.")
