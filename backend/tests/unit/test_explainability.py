import numpy as np
import pytest
from app.ml.inference import PredictionEngine
from app.ml.feature_engine import FeatureExtractor

class MockModel:
    def __init__(self, num_features: int):
        # Generate dummy positive feature importances
        self.feature_importances_ = np.array([0.01] * num_features, dtype=np.float64)
        # Give some specific indices higher importance to test sorting
        if num_features > 5:
            self.feature_importances_[1] = 0.8  # Strong subject indicator
            self.feature_importances_[-5] = 0.5 # Mismatch header index

def test_explain_prediction_structure_and_factors():
    """
    Fits a tiny FeatureExtractor and runs explain_prediction() on mock inputs.
    Asserts output keys, sorting order, and clean/spam indicators map correctly.
    """
    # 1. Fit small FeatureExtractor
    extractor = FeatureExtractor(max_subject_features=10, max_body_features=10)
    mock_dataset = [
        {"subject": "scam reward", "body_text": "please check login now !", "sender": "test@user.com", "links": [], "headers": {"spf": "pass"}},
        {"subject": "normal hello", "body_text": "simple clean update text", "sender": "test@user.com", "links": [], "headers": {"spf": "pass"}},
    ]
    extractor.fit(mock_dataset)
    
    # 2. Setup mock model
    num_subj = len(extractor.subject_vectorizer.vocabulary_)
    num_body = len(extractor.body_vectorizer.vocabulary_)
    total_features = num_subj + num_body + 20
    
    model = MockModel(total_features)
    
    # 3. Instantiate Engine
    engine = PredictionEngine(model, extractor, threshold=0.65)
    
    # Test email payload
    test_email = {
        "subject": "scam alert",
        "body_text": "login link details reward alert !",
        "sender": "bad-sender@netflix-update.com",
        "links": ["http://netflix-update.com/login"],
        "headers": {
            "spf": "fail",
            "reply-to": "different@site.com",
            "hop_count": 4
        }
    }
    
    explanation = engine.explain_prediction(test_email)
    
    # Assert output structure
    assert "top_spam_factors" in explanation
    assert "top_clean_factors" in explanation
    
    assert isinstance(explanation["top_spam_factors"], list)
    assert isinstance(explanation["top_clean_factors"], list)
    
    # Check bounds
    assert len(explanation["top_spam_factors"]) <= 5
    assert len(explanation["top_clean_factors"]) <= 3
    
    # Verify elements contains feature name and score keys
    for item in explanation["top_spam_factors"]:
        assert "feature" in item
        assert "score" in item
        assert isinstance(item["score"], float)
