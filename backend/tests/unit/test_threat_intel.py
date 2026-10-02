import pytest
from app.services.threat_intel import threat_intel
from app.database.collections import get_collection

def test_threat_intel_heuristics_and_caching(require_db):
    """
    Verifies that the threat intelligence reputation engine accurately identifies
    clean, suspicious, and malicious domains, and checks MongoDB caching logs.
    """
    cache_col = get_collection("threat_intel_cache")
    cache_col.delete_many({})
    
    # 1. Test clean domain reputation
    rep_clean = threat_intel.check_domain_reputation("google.com")
    assert rep_clean["verdict"] == "clean"
    assert rep_clean["threat_score"] == 0.0
    
    # 2. Test blacklisted domain reputation
    rep_mal = threat_intel.check_domain_reputation("netflix-update.com")
    assert rep_mal["verdict"] == "malicious"
    assert rep_mal["threat_score"] == 1.0
    
    # 3. Test suspicious heuristic pattern domain
    rep_susp = threat_intel.check_domain_reputation("verify-account-portal.xyz")
    assert rep_susp["verdict"] == "suspicious"
    assert rep_susp["threat_score"] >= 0.50
    
    # 4. Assert entries are recorded in database cache
    cached_docs = list(cache_col.find({}))
    assert len(cached_docs) == 3
    
    # Test caching performance (calling second time retrieves cached version)
    rep_clean_cached = threat_intel.check_domain_reputation("google.com")
    assert rep_clean_cached["verdict"] == "clean"
    assert rep_clean_cached["threat_score"] == 0.0
    
    # 5. Test inspect_urls batch checks
    urls = [
        "https://google.com/search?q=test",
        "http://netflix-update.com/login",
        "http://verify-account-portal.xyz/secure"
    ]
    report = threat_intel.inspect_urls(urls)
    
    assert report["is_malicious"] is True
    assert report["highest_threat_score"] == 1.0
    assert report["checked_urls_count"] == 3
    assert len(report["flagged_urls"]) == 2
    
    flagged_domains = [item["domain"] for item in report["flagged_urls"]]
    assert "netflix-update.com" in flagged_domains
    assert "verify-account-portal.xyz" in flagged_domains
