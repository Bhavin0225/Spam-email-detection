import os
import shutil
import tempfile
import numpy as np
import pandas as pd
import pytest
from app.ml.feature_engine import FeatureExtractor, extract_email_address

def test_extract_email_address():
    assert extract_email_address('"Netflix Billing" <renewals@netflix-billing.com>') == "renewals@netflix-billing.com"
    assert extract_email_address("renewals@netflix-billing.com") == "renewals@netflix-billing.com"
    assert extract_email_address("") == ""

def test_feature_extractor_dimensions():
    emails = [
        {"subject": "Urgent Netflix alert", "body_text": "Please update netflix login details.", "sender": "renewals@netflix.com"},
        {"subject": "Work updates", "body_text": "Please review the document attached.", "sender": "boss@office.com"}
    ]
    
    extractor = FeatureExtractor(max_subject_features=5, max_body_features=10)
    extractor.fit(emails)
    
    assert extractor.is_fitted
    
    # transform single email
    features = extractor.transform(emails[0])
    # Expected shape: subject vocabulary + body vocabulary + 20 handcrafted features
    vocab_subj_len = len(extractor.subject_vectorizer.vocabulary_)
    vocab_body_len = len(extractor.body_vectorizer.vocabulary_)
    expected_dim = vocab_subj_len + vocab_body_len + 20
    assert features.shape == (expected_dim,)
    assert isinstance(features, np.ndarray)
    
    # transform batch
    batch_features = extractor.transform_batch(emails)
    assert batch_features.shape == (2, expected_dim)

def test_url_features_extraction():
    extractor = FeatureExtractor()
    
    # Scenario A: No URLs
    email_no_urls = {
        "subject": "", "body_text": "Plain text with no URLs.", "sender": "",
        "links": [], "headers": {}
    }
    features_a = extractor.extract_handcrafted_features(email_no_urls)
    assert features_a[0] == 0.0  # url_count
    assert features_a[1] == 0.0  # avg_url_length
    assert features_a[2] == 0.0  # has_ip_domain
    assert features_a[3] == 0.0  # has_shortener
    assert features_a[4] == 0.0  # suspicious_keyword_count
    assert features_a[5] == 0.0  # https_ratio
    
    # Scenario B: URLs with IP, shortener, keywords
    email_suspicious_urls = {
        "subject": "", "body_text": "", "sender": "",
        "links": [
            "http://192.168.1.100/verify-login",
            "https://bit.ly/345-secure"
        ],
        "headers": {}
    }
    features_b = extractor.extract_handcrafted_features(email_suspicious_urls)
    assert features_b[0] == 2.0   # url_count
    assert features_b[1] == float((len(email_suspicious_urls["links"][0]) + len(email_suspicious_urls["links"][1])) / 2.0) # avg length
    assert features_b[2] == 1.0   # has_ip_domain (IP address in first URL)
    assert features_b[3] == 1.0   # has_shortener (bit.ly in second URL)
    # keywords matched: "verify", "login", "secure" -> 3.0
    assert features_b[4] == 3.0   
    assert features_b[5] == 0.5   # https_ratio (1 out of 2 is https)

def test_header_features_extraction():
    extractor = FeatureExtractor()
    
    # Scenario A: SPF and DKIM pass, matching Reply-To
    email_passing = {
        "subject": "", "body_text": "", "sender": "service@paypal.com",
        "links": [],
        "headers": {
            "spf": "pass (google.com: domain of service@paypal.com)",
            "dkim": "v=1; a=rsa-sha256; d=paypal.com; s=s2048;",
            "dmarc": "pass",
            "reply-to": "service@paypal.com",
            "hop_count": 4
        }
    }
    features_a = extractor.extract_handcrafted_features(email_passing)
    assert features_a[6] == 1.0   # spf_pass
    assert features_a[7] == 1.0   # dkim_pass
    assert features_a[8] == 1.0   # dmarc_pass
    assert features_a[9] == 0.0   # reply_to_mismatch (identical emails)
    assert features_a[10] == 4.0  # hop_count
    
    # Scenario B: Fails and mismatches
    email_failing = {
        "subject": "", "body_text": "", "sender": "service@paypal.com",
        "links": [],
        "headers": {
            "spf": "fail",
            "dkim": "",
            "dmarc": "fail",
            "reply-to": "attacker@scam-mail.net",
            "hop_count": 0
        }
    }
    features_b = extractor.extract_handcrafted_features(email_failing)
    assert features_b[6] == 0.0   # spf_pass
    assert features_b[7] == 0.0   # dkim_pass
    assert features_b[8] == 0.0   # dmarc_pass
    assert features_b[9] == 1.0   # reply_to_mismatch (different emails)
    assert features_b[10] == 0.0  # hop_count

def test_statistical_features_extraction():
    extractor = FeatureExtractor()
    
    # Character count: 12, uppercase: 2 (T, E), special: 2 (!, !), spaces: 2
    body = "Test Email!!"
    email = {
        "subject": "", "body_text": body, "sender": "",
        "links": [], "headers": {}
    }
    
    features = extractor.extract_handcrafted_features(email)
    assert features[11] == 12.0                  # body_length
    assert features[12] == 2.0                   # word_count
    assert features[13] == float(2.0 / 12.0)     # capital_ratio (T, E)
    assert features[14] == float(2.0 / 12.0)     # special_char_ratio (!, !)
    assert features[15] == 2.0                   # exclamation_count

def test_feature_extractor_persistence():
    emails = [
        {"subject": "Urgent Net Netflix", "body_text": "Verify netnetflix updates login !!", "sender": "alert@netflix.com"},
        {"subject": "Team weekend agenda", "body_text": "Meeting will start on Saturday afternoon.", "sender": "manager@office.com"}
    ]
    
    extractor = FeatureExtractor(max_subject_features=5, max_body_features=5)
    extractor.fit(emails)
    
    original_vector = extractor.transform(emails[0])
    
    # Create temp directory to save
    temp_dir = tempfile.mkdtemp()
    try:
        extractor.save(temp_dir)
        
        # Load in a new extractor
        loaded_extractor = FeatureExtractor()
        loaded_extractor.load(temp_dir)
        
        # Assertions
        assert loaded_extractor.is_fitted
        assert loaded_extractor.max_subject_features == 5
        assert loaded_extractor.max_body_features == 5
        
        loaded_vector = loaded_extractor.transform(emails[0])
        np.testing.assert_array_almost_equal(original_vector, loaded_vector)
    finally:
        shutil.rmtree(temp_dir)
