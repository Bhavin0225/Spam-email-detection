import pytest
from app.database.collections import get_collection
from scripts.fetch_spamassassin import generate_mock as sa_mock
from scripts.fetch_enron import generate_mock as en_mock
from scripts.fetch_phishtank import generate_mock as pt_mock
from scripts.ingest_data import ingest_pipeline

def test_ingestion_pipeline_runs_and_populates_db(require_db):
    """
    Triggers local mock dataset directories creation, executes master ingestion,
    and asserts DB count increases, train/val/test splits, and metadata logs.
    """
    # 1. Prepare Mock Data Files
    sa_mock()
    en_mock()
    pt_mock()

    # Clear prior collection state to run tests on a clean slate
    emails_col = get_collection("emails")
    meta_col = get_collection("dataset_metadata")
    emails_col.delete_many({})
    meta_col.delete_many({})

    # 2. Run Ingestion Pipeline
    ingest_pipeline()

    # 3. Assert Storage
    total_emails = emails_col.count_documents({})
    # Mock counts: SpamAssassin (3 ham, 3 spam), Enron (3 ham, 3 spam), PhishTank (5 phishing)
    # Total expected emails = 6 + 6 + 5 = 17 records
    assert total_emails == 17

    total_meta = meta_col.count_documents({})
    assert total_meta == 3  # SpamAssassin, Enron, PhishTank metadata registries

    # 4. Verify split ratios for SpamAssassin (6 items)
    # Train 70% (4 items), Val 15% (1 item), Test 15% (1 item)
    sa_emails = list(emails_col.find({"dataset_source": "SpamAssassin"}))
    splits = [e["split"] for e in sa_emails]
    
    assert splits.count("train") == 4
    assert splits.count("validation") == 1
    assert splits.count("test") == 1

    # 5. Verify Deduplication Block (Running a second time inserts 0 duplicates)
    ingest_pipeline()
    assert emails_col.count_documents({}) == 17  # remains unchanged
