import os
from scripts.fetch_spamassassin import generate_mock as sa_mock, DATA_DIR as SA_DIR
from scripts.fetch_enron import generate_mock as en_mock, DATA_DIR as EN_DIR
from scripts.fetch_phishtank import generate_mock as pt_mock, DATA_DIR as PT_DIR

def test_fetch_scripts_mock_generation():
    """
    Verifies that running the mock functions creates raw email structures and PhishTank JSONs
    inside the target directories.
    """
    # 1. Verify SpamAssassin Mocks
    sa_mock()
    assert os.path.exists(os.path.join(SA_DIR, "easy_ham"))
    assert os.path.exists(os.path.join(SA_DIR, "spam"))
    assert len(os.listdir(os.path.join(SA_DIR, "easy_ham"))) > 0
    assert len(os.listdir(os.path.join(SA_DIR, "spam"))) > 0

    # 2. Verify Enron Mocks
    en_mock()
    assert os.path.exists(os.path.join(EN_DIR, "enron1", "ham"))
    assert os.path.exists(os.path.join(EN_DIR, "enron1", "spam"))
    assert len(os.listdir(os.path.join(EN_DIR, "enron1", "ham"))) > 0
    assert len(os.listdir(os.path.join(EN_DIR, "enron1", "spam"))) > 0

    # 3. Verify PhishTank Mocks
    pt_mock()
    pt_json = os.path.join(PT_DIR, "online-valid.json")
    assert os.path.exists(pt_json)
    with open(pt_json, "r", encoding="utf-8") as f:
        content = f.read()
        assert "phish_id" in content
        assert "PayPal" in content
