import numpy as np
from app.ml.feature_engine import FeatureExtractor

class PredictionEngine:
    """
    ML Inference Engine that performs feature extraction and classification using the trained XGBoost model.
    """
    def __init__(self, model, extractor: FeatureExtractor, threshold: float = 0.65):
        self.model = model
        self.extractor = extractor
        self.threshold = threshold

    def predict(self, email_dict: dict) -> dict:
        """
        Extracts features and predicts spam likelihood class.
        Returns:
            dict containing prediction_label ('suspicious' or 'legitimate'), confidence, and risk_level.
        """
        # Transform raw email dict to combined dense feature vector
        features = self.extractor.transform(email_dict)
        
        # Backward compatibility for old models if new features were added to extractor
        if hasattr(self.model, "n_features_in_"):
            expected_features = self.model.n_features_in_
            if len(features) > expected_features:
                features = features[:expected_features]
            elif len(features) < expected_features:
                # pad with zeros if somehow smaller
                features = np.pad(features, (0, expected_features - len(features)), "constant")
                
        features_2d = features.reshape(1, -1)
        
        # Calculate posterior probabilities
        prob = float(self.model.predict_proba(features_2d)[0, 1])
        
        # Apply optimized decision threshold
        label = "suspicious" if prob >= self.threshold else "legitimate"
        
        # Derives threat risk bands
        if prob >= 0.85:
            risk_level = "high"
        elif prob >= self.threshold:
            risk_level = "medium"
        else:
            risk_level = "low"
            
        return {
            "prediction_label": label,
            "confidence": prob,
            "risk_level": risk_level
        }

    def explain_prediction(self, email_dict: dict) -> dict:
        """
        Calculates feature contributions (top spam and clean indicators) for a single email.
        """
        features = self.extractor.transform(email_dict)
        importances = self.model.feature_importances_
        
        # Calculate TF-IDF lengths
        num_subj = len(self.extractor.subject_vectorizer.vocabulary_)
        num_body = len(self.extractor.body_vectorizer.vocabulary_)
        
        # Get word vocab list mapping index -> word
        subj_words = self.extractor.subject_vectorizer.get_feature_names_out()
        body_words = self.extractor.body_vectorizer.get_feature_names_out()
        
        contributions = []
        
        # 1. Subject Words
        for idx in range(num_subj):
            val = features[idx]
            if val > 0:
                imp = float(importances[idx])
                contributions.append({
                    "name": f"Subject word '{subj_words[idx]}'",
                    "value": float(val),
                    "importance": imp,
                    "score": val * imp,
                    "type": "spam_indicator"
                })
                
        # 2. Body Words
        for idx in range(num_body):
            val = features[num_subj + idx]
            if val > 0:
                imp = float(importances[num_subj + idx])
                contributions.append({
                    "name": f"Body word '{body_words[idx]}'",
                    "value": float(val),
                    "importance": imp,
                    "score": val * imp,
                    "type": "spam_indicator"
                })
                
        # 3. Handcrafted features
        handcrafted_names = [
            ("Link count", "spam_indicator"),
            ("Average URL length", "spam_indicator"),
            ("IP address in link domain", "spam_indicator"),
            ("URL shortener in link", "spam_indicator"),
            ("Phishing keywords in links", "spam_indicator"),
            ("HTTPS links fraction", "clean_indicator"),
            ("SPF header authentication check", "clean_indicator"),
            ("DKIM header signature check", "clean_indicator"),
            ("DMARC header validation check", "clean_indicator"),
            ("Sender and Reply-To mismatch", "spam_indicator"),
            ("Hop count", "spam_indicator"),
            ("Email body length", "spam_indicator"),
            ("Body word count", "spam_indicator"),
            ("Uppercase character ratio", "spam_indicator"),
            ("Special character ratio", "spam_indicator"),
            ("Exclamation marks count", "spam_indicator"),
            ("Sender domain reputation score", "spam_indicator"),
            ("Email age in hours", "spam_indicator"),
            ("Has attachments flag", "spam_indicator"),
            ("Attachment risk score", "spam_indicator")
        ]
        
        for idx, (name, f_type) in enumerate(handcrafted_names):
            feature_idx = num_subj + num_body + idx
            if feature_idx < len(features) and feature_idx < len(importances):
                val = features[feature_idx]
                if val > 0:
                    imp = float(importances[feature_idx])
                    contributions.append({
                        "name": name,
                        "value": float(val),
                        "importance": imp,
                        "score": val * imp,
                        "type": f_type
                    })
                    
        # Sort contributions by score (value * importance) descending
        contributions.sort(key=lambda x: x["score"], reverse=True)
        
        # Split into spam indicators and clean indicators
        spam_ind = [c for c in contributions if c["type"] == "spam_indicator" and c["score"] > 0]
        clean_ind = [c for c in contributions if c["type"] == "clean_indicator"]
        
        # Fallback to general features if empty
        if not spam_ind:
            spam_ind = [{"name": "Overall language patterns", "score": 0.05}]
        if not clean_ind:
            clean_ind = [{"name": "Default security baseline checks", "score": 0.05}]
            
        return {
            "top_spam_factors": [{"feature": c["name"], "score": round(c["score"], 4)} for c in spam_ind[:5]],
            "top_clean_factors": [{"feature": c["name"], "score": round(c["score"], 4)} for c in clean_ind[:3]]
        }

