import os
import re
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from app.ml.preprocessor import clean_text
from app.utils.logger import logger

# List of known URL shorteners
SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "goo.gl", "rebrand.ly", "t.co", 
    "youtu.be", "tiny.cc", "ow.ly", "is.gd", "buff.ly", 
    "adf.ly", "bit.do", "mcaf.ee", "su.pr"
}

# Suspicious keywords in URLs
SUSPICIOUS_URL_KEYWORDS = {
    "login", "verify", "account", "secure", "update", 
    "signin", "banking", "confirm", "password", "billing", "support"
}

def extract_email_address(text: str) -> str:
    """
    Helper to extract a clean, lowercase email address from a header string.
    e.g., '"Netflix Billing" <renewals@netflix-billing.com>' -> 'renewals@netflix-billing.com'
    """
    if not text:
        return ""
    match = re.search(r"([\w.-]+@[\w.-]+)", text)
    if match:
        return match.group(1).lower().strip()
    return text.lower().strip()

class FeatureExtractor:
    """
    Feature engineering pipeline that extracts TF-IDF, URL, security header,
    and statistical character features from email records.
    """
    def __init__(self, max_subject_features: int = 1000, max_body_features: int = 3000):
        self.max_subject_features = max_subject_features
        self.max_body_features = max_body_features
        
        self.subject_vectorizer = TfidfVectorizer(max_features=self.max_subject_features)
        self.body_vectorizer = TfidfVectorizer(max_features=self.max_body_features)
        self.is_fitted = False

    def fit(self, emails_list_or_df) -> "FeatureExtractor":
        """
        Fits TF-IDF vectorizers on a list of email dictionaries or a pandas DataFrame.
        Only training split data should be fitted.
        """
        if isinstance(emails_list_or_df, pd.DataFrame):
            df = emails_list_or_df
        else:
            df = pd.DataFrame(emails_list_or_df)

        logger.info("Preprocessing subject and body text for TF-IDF fit...")
        
        # Extract and clean subjects/bodies
        clean_subjects = []
        clean_bodies = []
        
        for _, row in df.iterrows():
            clean_subjects.append(clean_text(row.get("subject", "")))
            clean_bodies.append(clean_text(row.get("body_text", "")))
            
        logger.info("Fitting subject TF-IDF vectorizer...")
        self.subject_vectorizer.fit(clean_subjects)
        
        logger.info("Fitting body TF-IDF vectorizer...")
        self.body_vectorizer.fit(clean_bodies)
        
        self.is_fitted = True
        logger.info("FeatureExtractor fitted successfully.")
        return self

    def extract_handcrafted_features(self, email: dict) -> np.ndarray:
        """
        Extracts hand-crafted URL, security header, statistical, and email provider features for a single email.
        Returns a 1D numpy array of size 20.
        """
        subject = email.get("subject", "") or ""
        body_text = email.get("body_text", "") or ""
        sender = email.get("sender", "") or ""
        links = email.get("links", []) or []
        headers = email.get("headers", {}) or {}

        # Ensure links is a list
        if not isinstance(links, list):
            links = []

        # --- 1. URL Features (6) ---
        url_count = len(links)
        avg_url_length = 0.0
        has_ip_domain = 0.0
        has_shortener = 0.0
        suspicious_keyword_count = 0.0
        https_ratio = 0.0

        if url_count > 0:
            avg_url_length = float(sum(len(u) for u in links) / url_count)
            
            # Count https occurrences
            https_ratio = float(sum(1 for u in links if u.lower().startswith("https")) / url_count)
            
            for u in links:
                u_lower = u.lower()
                # Check for IP address domain (e.g. http://192.168.1.1/login)
                if re.search(r"https?://(?:\d{1,3}\.){3}\d{1,3}", u_lower) or re.search(r"www\.(?:\d{1,3}\.){3}\d{1,3}", u_lower):
                    has_ip_domain = 1.0
                
                # Check for shorteners
                for domain in SHORTENER_DOMAINS:
                    if domain in u_lower:
                        has_shortener = 1.0
                        break
                
                # Count suspicious keywords in URLs
                for kw in SUSPICIOUS_URL_KEYWORDS:
                    if kw in u_lower:
                        suspicious_keyword_count += 1.0

        # --- 2. Header Features (5) ---
        spf_str = str(headers.get("spf", "")).lower()
        spf_pass = 1.0 if "pass" in spf_str else 0.0

        dkim_str = str(headers.get("dkim", "")).lower()
        dkim_pass = 0.0
        if dkim_str:
            if "pass" in dkim_str or "v=1" in dkim_str or "signature" in dkim_str:
                dkim_pass = 1.0

        dmarc_str = str(headers.get("dmarc", "")).lower()
        dmarc_pass = 1.0 if "pass" in dmarc_str else 0.0

        # Reply-To mismatch logic
        reply_to = str(headers.get("reply-to", ""))
        reply_to_mismatch = 0.0
        if reply_to:
            sender_email = extract_email_address(sender)
            reply_to_email = extract_email_address(reply_to)
            if reply_to_email and sender_email and (reply_to_email != sender_email):
                reply_to_mismatch = 1.0

        hop_count = float(headers.get("hop_count", 0.0))

        # --- 3. Statistical Features (5) ---
        body_length = float(len(body_text))
        word_count = float(len(body_text.split()))
        
        capital_ratio = 0.0
        special_char_ratio = 0.0
        exclamation_count = float(body_text.count("!"))

        if body_length > 0:
            uppercase_chars = sum(1 for c in body_text if c.isupper())
            capital_ratio = float(uppercase_chars / body_length)
            
            # Non-alphanumeric, non-space character count
            special_chars = sum(1 for c in body_text if not c.isalnum() and not c.isspace())
            special_char_ratio = float(special_chars / body_length)

        # --- 4. Accuracy Boosting Real Mailbox Features (4) ---
        # Feature 17: sender_reputation_score
        sender_reputation = 0.0
        sender_email = extract_email_address(sender)
        sender_domain = sender_email.split("@")[-1].lower() if "@" in sender_email else sender_email.lower()
        if sender_domain:
            try:
                from app.database.collections import get_collection
                predictions_col = get_collection("predictions")
                emails_col = get_collection("emails")
                email_records = list(emails_col.find({"sender_domain": sender_domain}, {"email_id": 1}))
                if email_records:
                    email_ids = [e["email_id"] for e in email_records]
                    total_preds = predictions_col.count_documents({"email_id": {"$in": email_ids}})
                    if total_preds > 0:
                        spam_preds = predictions_col.count_documents({
                            "email_id": {"$in": email_ids},
                            "prediction_label": "suspicious"
                        })
                        sender_reputation = float(spam_preds / total_preds)
            except Exception:
                sender_reputation = 0.0

        # Feature 18: email_age_hours
        email_age_hours = 0.0
        date_sent = email.get("date_sent")
        if date_sent:
            if isinstance(date_sent, str):
                try:
                    date_sent = datetime.fromisoformat(date_sent)
                except Exception:
                    date_sent = None
            if date_sent:
                now = datetime.now(timezone.utc)
                if date_sent.tzinfo is None:
                    date_sent = date_sent.replace(tzinfo=timezone.utc)
                diff = now - date_sent
                email_age_hours = max(0.0, float(diff.total_seconds() / 3600.0))

        # Feature 19: has_attachments
        attachments = email.get("attachments") or []
        has_attachments = 1.0 if len(attachments) > 0 else 0.0

        # Feature 20: attachment_risk_score
        attachment_risk_score = 0.0
        if attachments:
            max_risk = 0.0
            for att in attachments:
                filename = str(att.get("filename", "")).lower()
                content_type = str(att.get("content_type", "")).lower()
                risk = 0.0
                if filename.endswith(".exe") or filename.endswith(".bat") or filename.endswith(".cmd") or filename.endswith(".scr") or "x-msdownload" in content_type:
                    risk = 1.0
                elif filename.endswith(".zip") or filename.endswith(".rar") or filename.endswith(".7z") or filename.endswith(".tar") or filename.endswith(".gz") or "zip" in content_type or "compressed" in content_type:
                    risk = 0.8
                elif filename.endswith(".pdf") or "pdf" in content_type:
                    risk = 0.3
                elif filename.endswith(".docx") or filename.endswith(".doc") or filename.endswith(".xlsx") or filename.endswith(".xls") or "msword" in content_type or "officedocument" in content_type:
                    risk = 0.2
                else:
                    risk = 0.1
                if risk > max_risk:
                    max_risk = risk
            attachment_risk_score = max_risk

        return np.array([
            url_count, avg_url_length, has_ip_domain, has_shortener, suspicious_keyword_count, https_ratio,
            spf_pass, dkim_pass, dmarc_pass, reply_to_mismatch, hop_count,
            body_length, word_count, capital_ratio, special_char_ratio, exclamation_count,
            sender_reputation, email_age_hours, has_attachments, attachment_risk_score
        ], dtype=np.float64)

    def transform(self, email: dict) -> np.ndarray:
        """
        Transforms a single email dictionary into a combined dense feature vector.
        """
        if not self.is_fitted:
            raise RuntimeError("FeatureExtractor must be fitted before transforming data.")
            
        clean_subj = clean_text(email.get("subject", "") or "")
        clean_body = clean_text(email.get("body_text", "") or "")
        
        subj_tfidf = self.subject_vectorizer.transform([clean_subj]).toarray()[0]
        body_tfidf = self.body_vectorizer.transform([clean_body]).toarray()[0]
        
        handcrafted = self.extract_handcrafted_features(email)
        
        return np.concatenate([subj_tfidf, body_tfidf, handcrafted])

    def transform_batch(self, emails_list_or_df) -> np.ndarray:
        """
        Transforms a list/DataFrame of emails into a 2D numpy matrix of features.
        """
        if not self.is_fitted:
            raise RuntimeError("FeatureExtractor must be fitted before transforming data.")
            
        if isinstance(emails_list_or_df, pd.DataFrame):
            df = emails_list_or_df
        else:
            df = pd.DataFrame(emails_list_or_df)

        logger.info(f"Transforming batch of {len(df)} emails...")
        
        clean_subjects = []
        clean_bodies = []
        handcrafted_list = []
        
        for _, row in df.iterrows():
            email_dict = row.to_dict()
            clean_subjects.append(clean_text(email_dict.get("subject", "") or ""))
            clean_bodies.append(clean_text(email_dict.get("body_text", "") or ""))
            handcrafted_list.append(self.extract_handcrafted_features(email_dict))
            
        subj_tfidf_matrix = self.subject_vectorizer.transform(clean_subjects).toarray()
        body_tfidf_matrix = self.body_vectorizer.transform(clean_bodies).toarray()
        handcrafted_matrix = np.array(handcrafted_list, dtype=np.float64)
        
        return np.hstack([subj_tfidf_matrix, body_tfidf_matrix, handcrafted_matrix])

    def save(self, dir_path: str):
        """
        Serializes and saves the fitted vectorizer components to a given directory.
        """
        os.makedirs(dir_path, exist_ok=True)
        joblib.dump(self.subject_vectorizer, os.path.join(dir_path, "subject_vectorizer.pkl"))
        joblib.dump(self.body_vectorizer, os.path.join(dir_path, "body_vectorizer.pkl"))
        joblib.dump(self.is_fitted, os.path.join(dir_path, "is_fitted.pkl"))
        joblib.dump({
            "max_subject_features": self.max_subject_features,
            "max_body_features": self.max_body_features
        }, os.path.join(dir_path, "meta_config.pkl"))
        logger.info(f"Saved feature extractor components successfully under: {dir_path}")

    def load(self, dir_path: str) -> "FeatureExtractor":
        """
        Loads serialized vectorizer components from a given directory.
        """
        self.subject_vectorizer = joblib.load(os.path.join(dir_path, "subject_vectorizer.pkl"))
        self.body_vectorizer = joblib.load(os.path.join(dir_path, "body_vectorizer.pkl"))
        self.is_fitted = joblib.load(os.path.join(dir_path, "is_fitted.pkl"))
        meta = joblib.load(os.path.join(dir_path, "meta_config.pkl"))
        self.max_subject_features = meta.get("max_subject_features", 1000)
        self.max_body_features = meta.get("max_body_features", 3000)
        logger.info(f"Loaded feature extractor components successfully from: {dir_path}")
        return self

def test_feature_extraction():
    """
    CLI/Script helper to quickly test feature engineering extraction on a sample email.
    """
    extractor = FeatureExtractor(max_subject_features=10, max_body_features=20)
    
    sample_train_data = [
        {
            "subject": "Urgent Netflix Billing Billing",
            "body_text": "Verify your netnetflix billing at https://bit.ly/123 !! scam details",
            "sender": "alert@netflix.com"
        },
        {
            "subject": "Work meeting updates",
            "body_text": "Here is the plan for this weekend meeting",
            "sender": "boss@office.com"
        }
    ]
    
    extractor.fit(sample_train_data)
    
    test_email = {
        "subject": "Urgent Billing details required",
        "body_text": "Dear Netflix User, verify credentials at http://192.168.1.5/login immediately! !!",
        "sender": "netflix@scam-mail.com",
        "links": ["http://192.168.1.5/login"],
        "headers": {
            "spf": "softfail",
            "dkim": "",
            "dmarc": "fail",
            "reply-to": "badguy@hacker.com",
            "hop_count": 3
        }
    }
    
    features = extractor.transform(test_email)
    handcrafted = extractor.extract_handcrafted_features(test_email)
    
    print("--- Sample Email Feature Extraction Debug ---")
    print(f"Total Feature Size: {len(features)}")
    print(f"Handcrafted Features (Length 16): {handcrafted}")
    print("Feature array details:")
    print(f"  URL count: {handcrafted[0]} (Expected: 1)")
    print(f"  URL length: {handcrafted[1]} (Expected: ~26)")
    print(f"  Has IP domain: {handcrafted[2]} (Expected: 1.0)")
    print(f"  Has shortener: {handcrafted[3]} (Expected: 0.0)")
    print(f"  Suspicious keyword count: {handcrafted[4]} (Expected: 2.0 - login, verify)")
    print(f"  HTTPS ratio: {handcrafted[5]} (Expected: 0.0)")
    print(f"  SPF pass: {handcrafted[6]} (Expected: 0.0)")
    print(f"  DKIM pass: {handcrafted[7]} (Expected: 0.0)")
    print(f"  DMARC pass: {handcrafted[8]} (Expected: 0.0)")
    print(f"  Reply-To mismatch: {handcrafted[9]} (Expected: 1.0)")
    print(f"  Hop count: {handcrafted[10]} (Expected: 3.0)")
    print(f"  Body length: {handcrafted[11]} (Expected: ~74)")
    print(f"  Word count: {handcrafted[12]} (Expected: ~10)")
    print(f"  Capital ratio: {handcrafted[13]}")
    print(f"  Special character ratio: {handcrafted[14]}")
    print(f"  Exclamation count: {handcrafted[15]} (Expected: 3.0)")
