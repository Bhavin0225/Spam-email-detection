import os
import shutil
import tempfile
import numpy as np
import pytest
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
import joblib
from app.ml.training import optimize_decision_threshold

def get_risk_level(prob: float, threshold: float = 0.65) -> str:
    """
    Risk level derivation helper (based on decision threshold and confidence bands):
    - Confidence >= 0.85 -> "high"
    - Confidence >= threshold (0.65) -> "medium"
    - Confidence < threshold -> "low"
    """
    if prob >= 0.85:
        return "high"
    elif prob >= threshold:
        return "medium"
    else:
        return "low"

def test_model_training_fitting_and_predictions():
    # Create simple synthetic binary classification data
    X_train = np.array([
        [0.8, 0.9, 1.0],
        [0.7, 0.8, 0.9],
        [0.1, 0.2, 0.0],
        [0.0, 0.1, 0.2],
        [0.9, 0.9, 0.8],
        [0.2, 0.0, 0.1]
    ], dtype=np.float64)
    y_train = np.array([1, 1, 0, 0, 1, 0], dtype=np.int32)
    
    # MultinomialNB expects non-negative inputs
    nb = MultinomialNB()
    nb.fit(X_train, y_train)
    assert len(nb.predict(X_train)) == 6
    
    lr = LogisticRegression(random_state=42)
    lr.fit(X_train, y_train)
    assert len(lr.predict(X_train)) == 6
    
    xgb = XGBClassifier(eval_metric="logloss", random_state=42)
    xgb.fit(X_train, y_train)
    assert len(xgb.predict(X_train)) == 6

def test_threshold_tuning_logic():
    # Simple mockup model to check threshold optimization
    class MockModel:
        def predict_proba(self, X):
            # Returns probs where second column matches the input array values
            return np.hstack([1.0 - X, X])
            
    mock_model = MockModel()
    
    # 5 samples validation features (probs) and target labels
    # Using 0.6 instead of 0.1 to introduce a false positive at threshold < 0.6
    X_val = np.array([[0.6], [0.8], [0.2], [0.75], [0.9]], dtype=np.float64)
    y_val = np.array([0, 1, 0, 1, 1], dtype=np.int32)
    
    # Run optimizer
    best_t = optimize_decision_threshold(mock_model, X_val, y_val)
    
    assert isinstance(best_t, float)
    assert 0.30 <= best_t <= 0.90
    
    # High precision threshold expected (around 0.65 or above)
    assert best_t >= 0.60

def test_risk_level_derivation():
    # threshold default 0.65
    assert get_risk_level(0.90, 0.65) == "high"
    assert get_risk_level(0.70, 0.65) == "medium"
    assert get_risk_level(0.40, 0.65) == "low"
    
    # threshold custom 0.55
    assert get_risk_level(0.60, 0.55) == "medium"
    assert get_risk_level(0.50, 0.55) == "low"

def test_model_serialization_roundtrip():
    X_train = np.array([[0.5, 0.5], [0.1, 0.1]], dtype=np.float64)
    y_train = np.array([1, 0], dtype=np.int32)
    
    model = XGBClassifier(eval_metric="logloss", random_state=42)
    model.fit(X_train, y_train)
    
    orig_prob = model.predict_proba(X_train)
    
    temp_dir = tempfile.mkdtemp()
    try:
        model_path = os.path.join(temp_dir, "xgb.pkl")
        joblib.dump(model, model_path)
        
        # Load back
        loaded_model = joblib.load(model_path)
        loaded_prob = loaded_model.predict_proba(X_train)
        
        np.testing.assert_array_almost_equal(orig_prob, loaded_prob)
    finally:
        shutil.rmtree(temp_dir)
