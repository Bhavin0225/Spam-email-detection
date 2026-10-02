import os
import shutil
import tempfile
import pytest
from app.database.collections import get_collection
from scripts.fetch_spamassassin import generate_mock as sa_mock
from scripts.fetch_enron import generate_mock as en_mock
from scripts.fetch_phishtank import generate_mock as pt_mock
from scripts.ingest_data import ingest_pipeline
from app.ml.training import run_training_pipeline

def test_training_pipeline_db_integration(require_db):
    """
    Clears database collections, generates mock email directories, runs ingestion,
    triggers model training pipeline, and asserts saved pickle artifacts and logged database metadata.
    """
    # 1. Prepare Mock Data & Run Ingestion to populate splits in database
    sa_mock()
    en_mock()
    pt_mock()
    
    emails_col = get_collection("emails")
    meta_col = get_collection("dataset_metadata")
    model_meta_col = get_collection("model_metadata")
    
    emails_col.delete_many({})
    meta_col.delete_many({})
    model_meta_col.delete_many({})
    
    ingest_pipeline()
    
    # Assert database emails are present
    assert emails_col.count_documents({}) == 17
    
    # 2. Run Training Pipeline using temp directory for saved models
    temp_models_dir = tempfile.mkdtemp()
    try:
        results = run_training_pipeline(model_version="v1.0.0", models_dir=temp_models_dir)
        
        assert results["version"] == "v1.0.0"
        assert "nb" in results
        assert "lr" in results
        assert "xgb" in results
        assert results["xgb"]["threshold"] >= 0.30
        
        # 3. Assert Serialized Artifacts Exist
        model_save_path = os.path.join(temp_models_dir, "v1.0.0", "xgboost_model.pkl")
        assert os.path.exists(model_save_path), "XGBoost model pickle file was not created!"
        
        # 4. Assert Database model_metadata Records exist
        metadata_records = list(model_meta_col.find({}))
        assert len(metadata_records) == 1
        
        record = metadata_records[0]
        assert record["model_version"] == "v1.0.0"
        assert record["algorithm"] == "XGBoost"
        assert isinstance(record["precision"], float)
        assert isinstance(record["recall"], float)
        assert isinstance(record["f1_score"], float)
        assert isinstance(record["auc_roc"], float)
        assert isinstance(record["threshold"], float)
        assert record["deployed"] is True
        assert "v1.0.0/" in record["artifact_path"]
        
    finally:
        shutil.rmtree(temp_models_dir)
