import pytest
from app.database.connection import db_manager

def test_database_indexes_configuration(require_db):
    """
    Verifies that all 27 custom indexes across 7 collections are correctly configured in MongoDB.
    Specifically checks names, uniqueness constraints, key lists, and TTL policies.
    """
    db = db_manager.db

    def get_indices_info(collection_name: str) -> dict:
        return db[collection_name].index_information()

    # 1. users Collection Indexes (3)
    users_indexes = get_indices_info("users")
    assert "idx_users_email" in users_indexes
    assert users_indexes["idx_users_email"].get("unique") is True
    assert users_indexes["idx_users_email"]["key"] == [("email", 1)]

    assert "idx_users_user_id" in users_indexes
    assert users_indexes["idx_users_user_id"].get("unique") is True
    assert users_indexes["idx_users_user_id"]["key"] == [("user_id", 1)]

    assert "idx_users_role" in users_indexes
    assert users_indexes["idx_users_role"]["key"] == [("role", 1)]

    # 2. emails Collection Indexes (7)
    emails_indexes = get_indices_info("emails")
    assert "idx_emails_email_id" in emails_indexes
    assert emails_indexes["idx_emails_email_id"].get("unique") is True
    assert emails_indexes["idx_emails_email_id"]["key"] == [("email_id", 1)]

    assert "idx_emails_created_at" in emails_indexes
    assert emails_indexes["idx_emails_created_at"]["key"] == [("created_at", -1)]

    assert "idx_emails_sender_domain" in emails_indexes
    assert emails_indexes["idx_emails_sender_domain"]["key"] == [("sender_domain", 1)]

    assert "idx_emails_dataset_source" in emails_indexes
    assert emails_indexes["idx_emails_dataset_source"]["key"] == [("dataset_source", 1)]

    assert "idx_emails_split" in emails_indexes
    assert emails_indexes["idx_emails_split"]["key"] == [("split", 1)]

    assert "idx_emails_label" in emails_indexes
    assert emails_indexes["idx_emails_label"]["key"] == [("label", 1)]

    assert "idx_emails_content_hash" in emails_indexes
    assert emails_indexes["idx_emails_content_hash"].get("unique") is True
    assert emails_indexes["idx_emails_content_hash"]["key"] == [("content_hash", 1)]

    # 3. predictions Collection Indexes (5)
    pred_indexes = get_indices_info("predictions")
    assert "idx_predictions_prediction_id" in pred_indexes
    assert pred_indexes["idx_predictions_prediction_id"].get("unique") is True
    assert pred_indexes["idx_predictions_prediction_id"]["key"] == [("prediction_id", 1)]

    assert "idx_predictions_email_id" in pred_indexes
    assert pred_indexes["idx_predictions_email_id"]["key"] == [("email_id", 1)]

    assert "idx_predictions_model_version" in pred_indexes
    assert pred_indexes["idx_predictions_model_version"]["key"] == [("model_version", 1)]

    assert "idx_predictions_created_at" in pred_indexes
    assert pred_indexes["idx_predictions_created_at"]["key"] == [("created_at", -1)]

    assert "idx_predictions_user_id" in pred_indexes
    assert pred_indexes["idx_predictions_user_id"]["key"] == [("user_id", 1)]

    # 4. feedback Collection Indexes (4)
    feedback_indexes = get_indices_info("feedback")
    assert "idx_feedback_feedback_id" in feedback_indexes
    assert feedback_indexes["idx_feedback_feedback_id"].get("unique") is True
    assert feedback_indexes["idx_feedback_feedback_id"]["key"] == [("feedback_id", 1)]

    assert "idx_feedback_prediction_id" in feedback_indexes
    assert feedback_indexes["idx_feedback_prediction_id"]["key"] == [("prediction_id", 1)]

    assert "idx_feedback_user_id" in feedback_indexes
    assert feedback_indexes["idx_feedback_user_id"]["key"] == [("user_id", 1)]

    assert "idx_feedback_status" in feedback_indexes
    assert feedback_indexes["idx_feedback_status"]["key"] == [("status", 1)]

    # 5. model_metadata Collection Indexes (2)
    model_indexes = get_indices_info("model_metadata")
    assert "idx_model_version" in model_indexes
    assert model_indexes["idx_model_version"].get("unique") is True
    assert model_indexes["idx_model_version"]["key"] == [("model_version", 1)]

    assert "idx_model_deployed" in model_indexes
    assert model_indexes["idx_model_deployed"]["key"] == [("deployed", 1)]

    # 6. dataset_metadata Collection Indexes (4)
    dataset_indexes = get_indices_info("dataset_metadata")
    assert "idx_dataset_id" in dataset_indexes
    assert dataset_indexes["idx_dataset_id"].get("unique") is True
    assert dataset_indexes["idx_dataset_id"]["key"] == [("dataset_id", 1)]

    assert "idx_dataset_name" in dataset_indexes
    assert dataset_indexes["idx_dataset_name"]["key"] == [("name", 1)]

    assert "idx_dataset_source" in dataset_indexes
    assert dataset_indexes["idx_dataset_source"]["key"] == [("source", 1)]

    assert "idx_dataset_ingestion_date" in dataset_indexes
    assert dataset_indexes["idx_dataset_ingestion_date"]["key"] == [("ingestion_date", -1)]

    # 7. system_logs Collection Indexes (5)
    logs_indexes = get_indices_info("system_logs")
    assert "idx_logs_log_id" in logs_indexes
    assert logs_indexes["idx_logs_log_id"].get("unique") is True
    assert logs_indexes["idx_logs_log_id"]["key"] == [("log_id", 1)]

    assert "idx_logs_event_type" in logs_indexes
    assert logs_indexes["idx_logs_event_type"]["key"] == [("event_type", 1)]

    assert "idx_logs_timestamp" in logs_indexes
    assert logs_indexes["idx_logs_timestamp"]["key"] == [("timestamp", -1)]

    assert "idx_logs_severity" in logs_indexes
    assert logs_indexes["idx_logs_severity"]["key"] == [("severity", 1)]

    # Verify TTL config
    assert "idx_logs_ttl" in logs_indexes
    assert logs_indexes["idx_logs_ttl"]["key"] == [("timestamp", 1)]
    assert logs_indexes["idx_logs_ttl"].get("expireAfterSeconds") == 90 * 24 * 60 * 60
