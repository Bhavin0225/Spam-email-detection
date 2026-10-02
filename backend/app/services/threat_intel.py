import re
from datetime import datetime, timezone
from urllib.parse import urlparse
from app.database.collections import get_collection
from app.utils.logger import logger

# List of simulated malicious domains
MALICIOUS_DOMAINS = {
    "netflix-update.com",
    "paypal-security.com",
    "login-verification.xyz",
    "secure-bank-login.net",
    "verify-account-info.org",
    "netflix-billing.com",
    "paypal-signin.com",
    "update-account-details.xyz",
    "verify-appleid.info"
}

# Suspicious words often found in phishing subdomains or domains
SUSPICIOUS_KEYWORDS = {"login", "verify", "secure", "update", "account", "signin", "billing"}

class ThreatIntelService:
    """
    Threat Intelligence Reputation Service. Inspects body links, maps domains
    against known blacklists or heuristics, and caches lookups in MongoDB.
    """
    def __init__(self):
        self._initialized_indices = False

    def _ensure_indices(self, col):
        if not self._initialized_indices:
            try:
                col.create_index("domain", unique=True)
                col.create_index("created_at", expireAfterSeconds=86400) # TTL of 24h
                self._initialized_indices = True
            except Exception as e:
                logger.error(f"Failed to create indices on threat_intel_cache: {str(e)}")

    def check_domain_reputation(self, domain: str) -> dict:
        """
        Runs heuristics and lookups for a single domain. Caches the result in MongoDB.
        """
        domain = domain.strip().lower()
        if not domain:
            return {"domain": "", "verdict": "clean", "threat_score": 0.0, "reason": "Empty domain"}

        cache_col = get_collection("threat_intel_cache")
        self._ensure_indices(cache_col)

        # 1. Query Cache
        cached_record = cache_col.find_one({"domain": domain})
        if cached_record:
            return cached_record

        # 2. Heuristics & Blacklist Checks
        verdict = "clean"
        threat_score = 0.0
        reason = "Domain is clear"

        if domain in MALICIOUS_DOMAINS:
            verdict = "malicious"
            threat_score = 1.0
            reason = "Matches known threat intelligence blacklist signature"
        else:
            # Check suspicious keyword count in domain
            matched_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in domain]
            has_suspicious_tld = domain.endswith((".xyz", ".info", ".click", ".top", ".work"))
            has_many_hyphens = domain.count("-") >= 3

            if matched_keywords and (has_suspicious_tld or has_many_hyphens):
                verdict = "suspicious"
                threat_score = 0.75
                reason = f"Contains suspicious phishing terms {matched_keywords} and flags abnormal structural indicators"
            elif has_suspicious_tld and has_many_hyphens:
                verdict = "suspicious"
                threat_score = 0.60
                reason = "Domain features generic TLD and multiple hyphen delimiters"
            elif len(matched_keywords) >= 2:
                verdict = "suspicious"
                threat_score = 0.50
                reason = f"Multiple credential-theft keywords detected: {matched_keywords}"

        # 3. Store in Cache
        record = {
            "domain": domain,
            "verdict": verdict,
            "threat_score": threat_score,
            "reason": reason,
            "created_at": datetime.now(timezone.utc)
        }
        
        try:
            cache_col.insert_one(record)
        except Exception as e:
            # Handle unique key duplicate writing gracefully
            logger.debug(f"Cache write ignored: {str(e)}")

        if "_id" in record:
            record.pop("_id")
        return record

    def inspect_urls(self, urls: list) -> dict:
        """
        Inspects a list of URLs, calculates checks, and returns a compiled threat report.
        """
        flagged_urls = []
        highest_score = 0.0
        is_malicious = False

        checked_domains = set()

        for url in urls:
            try:
                parsed = urlparse(url)
                netloc = parsed.netloc or parsed.path # Fallback if missing scheme
                # Strip port if present
                domain = netloc.split(":")[0].lower()
                
                if not domain or domain in checked_domains:
                    continue
                checked_domains.add(domain)

                rep = self.check_domain_reputation(domain)
                
                if rep["threat_score"] > highest_score:
                    highest_score = rep["threat_score"]
                
                if rep["verdict"] in {"malicious", "suspicious"}:
                    if rep["verdict"] == "malicious":
                        is_malicious = True
                    flagged_urls.append({
                        "url": url,
                        "domain": domain,
                        "verdict": rep["verdict"],
                        "threat_score": rep["threat_score"],
                        "reason": rep["reason"]
                    })
            except Exception as e:
                logger.warning(f"Failed parsing URL '{url}': {str(e)}")

        return {
            "is_malicious": is_malicious or highest_score >= 0.75,
            "highest_threat_score": highest_score,
            "checked_urls_count": len(checked_domains),
            "flagged_urls": flagged_urls
        }

# Singleton Instance
threat_intel = ThreatIntelService()
