import tempfile
import shutil
import numpy as np
import pandas as pd
import pytest
from app.database.collections import get_collection
from app.ml.feature_engine import FeatureExtractor
from scripts.fetch_spamassassin import generate_mock as sa_mock
from scripts.fetch_enron import generate_mock as en_mock
from scripts.fetch_phishtank import generate_mock as pt_mock
from scripts.ingest_data import ingest_pipeline

def test_feature_pipeline_db_integration(require_db):
    """
    Retrieves ingested emails from the database, fits the FeatureExtractor on the
    training split, transforms train and validation sets, and asserts no missing
    features, exact dimensions, and joblib loading compatibility.
    """
    # 1. Prepare Mock Data & Run Ingestion to ensure database is populated
    sa_mock()
    en_mock()
    pt_mock()
    
    emails_col = get_collection("emails")
    meta_col = get_collection("dataset_metadata")
    emails_col.delete_many({})
    meta_col.delete_many({})
    
    ingest_pipeline()

    # Retrieve emails
    db_emails = list(emails_col.find({}))
    df = pd.DataFrame(db_emails)
    
    # Check splits
    train_df = df[df["split"] == "train"]
    val_df = df[df["split"] == "validation"]
    
    if len(train_df) == 0:
        pytest.skip("No training emails found in the database. Ingestion must split data correctly.")
        
    # Fit FeatureExtractor on training split
    extractor = FeatureExtractor(max_subject_features=20, max_body_features=50)
    extractor.fit(train_df)
    
    assert extractor.is_fitted
    
    # Transform train and validation sets
    train_features = extractor.transform_batch(train_df)
    val_features = extractor.transform_batch(val_df)
    
    # Assert dimensions
    # Total subject (20) + body (50) + handcrafted (20) = 90 features
    assert train_features.shape == (len(train_df), 90)
    assert val_features.shape == (len(val_df), 90)
    
    # Assert no NaN or inf values
    assert not np.isnan(train_features).any(), "Train features contain NaN values!"
    assert not np.isnan(val_features).any(), "Validation features contain NaN values!"
    assert not np.isinf(train_features).any(), "Train features contain infinite values!"
    assert not np.isinf(val_features).any(), "Validation features contain infinite values!"
    
    # Verify save & load roundtrip
    temp_dir = tempfile.mkdtemp()
    try:
        extractor.save(temp_dir)
        
        # Load in new extractor
        new_extractor = FeatureExtractor()
        new_extractor.load(temp_dir)
        
        # Select one email from database to test
        sample_email = train_df.iloc[0].to_dict()
        original_vec = extractor.transform(sample_email)
        loaded_vec = new_extractor.transform(sample_email)
        
        np.testing.assert_array_almost_equal(original_vec, loaded_vec)
        assert len(loaded_vec) == 90
    finally:
        shutil.rmtree(temp_dir)
