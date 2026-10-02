from app.database.connection import db_manager

def test_database_collections_exist(require_db):
    """
    Verifies that all 7 required collections have been successfully created on database initialization.
    """
    required_collections = {
        "users",
        "emails",
        "predictions",
        "feedback",
        "model_metadata",
        "dataset_metadata",
        "system_logs"
    }

    db = db_manager.db
    existing_collections = set(db.list_collection_names())

    for collection in required_collections:
        assert collection in existing_collections, f"Collection '{collection}' is missing from the database."
