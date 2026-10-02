import numpy as np
import pytest
from app.ml.inference import PredictionEngine

class MockClassifier:
    def __init__(self, spam_prob: float):
        self.spam_prob = spam_prob

    def predict_proba(self, X):
        return np.array([[1.0 - self.spam_prob, self.spam_prob]])

class MockFeatureExtractor:
    def transform(self, email_dict: dict):
        return np.array([0.1, 0.2, 0.3])

def test_prediction_engine_thresholds_and_risk():
    # 1. High Risk case (prob >= 0.85)
    engine = PredictionEngine(MockClassifier(0.90), MockFeatureExtractor(), threshold=0.65)
    res = engine.predict({"subject": "Scam Alert", "body_text": "Please verify", "sender": "bad@site.com"})
    assert res["prediction_label"] == "suspicious"
    assert res["confidence"] == 0.90
    assert res["risk_level"] == "high"

    # 2. Medium Risk case (threshold <= prob < 0.85)
    engine = PredictionEngine(MockClassifier(0.70), MockFeatureExtractor(), threshold=0.65)
    res = engine.predict({"subject": "Scam Alert", "body_text": "Please verify", "sender": "bad@site.com"})
    assert res["prediction_label"] == "suspicious"
    assert res["confidence"] == 0.70
    assert res["risk_level"] == "medium"

    # 3. Low Risk case (prob < threshold)
    engine = PredictionEngine(MockClassifier(0.40), MockFeatureExtractor(), threshold=0.65)
    res = engine.predict({"subject": "Scam Alert", "body_text": "Please verify", "sender": "bad@site.com"})
    assert res["prediction_label"] == "legitimate"
    assert res["confidence"] == 0.40
    assert res["risk_level"] == "low"
