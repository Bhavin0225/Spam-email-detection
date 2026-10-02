import os
import sys
import json
import urllib.request
import argparse

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "phishtank")

def download_phishtank():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    url = "http://data.phishtank.com/data/online-valid.json"
    target_path = os.path.join(DATA_DIR, "online-valid.json")
    
    print(f"Downloading PhishTank active phishing entries from {url}...")
    try:
        # Request with a custom User-Agent to prevent 403 access blocks from PhishTank
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "phishtank/spam_detection_system_agent"}
        )
        
        with urllib.request.urlopen(req) as response:
            data = response.read()
            with open(target_path, "wb") as f:
                f.write(data)
                
        print("Downloaded PhishTank verified active list successfully.")
    except Exception as e:
        print(f"ERROR: Failed to fetch PhishTank active JSON: {str(e)}", file=sys.stderr)
        print("Please consider running with --mock to run tests in offline environments.", file=sys.stderr)
        sys.exit(1)

def generate_mock():
    os.makedirs(DATA_DIR, exist_ok=True)
    target_path = os.path.join(DATA_DIR, "online-valid.json")
    
    mock_data = [
        {
            "phish_id": "100001",
            "url": "http://paypal-verification-portal-update.com/login",
            "phish_detail_url": "https://www.phishtank.com/phish_detail.php?phish_id=100001",
            "submission_time": "2026-06-07T12:00:00+00:00",
            "verified": "yes",
            "online": "yes",
            "target": "PayPal"
        },
        {
            "phish_id": "100002",
            "url": "http://netflix-billing-renewal-support.net/confirm",
            "phish_detail_url": "https://www.phishtank.com/phish_detail.php?phish_id=100002",
            "submission_time": "2026-06-07T12:01:00+00:00",
            "verified": "yes",
            "online": "yes",
            "target": "Netflix"
        },
        {
            "phish_id": "100003",
            "url": "http://chase-bank-verify-your-account.org/login.php",
            "phish_detail_url": "https://www.phishtank.com/phish_detail.php?phish_id=100003",
            "submission_time": "2026-06-07T12:02:00+00:00",
            "verified": "yes",
            "online": "yes",
            "target": "Chase Bank"
        },
        {
            "phish_id": "100004",
            "url": "http://secure-login-microsoft-auth-update.info/home",
            "phish_detail_url": "https://www.phishtank.com/phish_detail.php?phish_id=100004",
            "submission_time": "2026-06-07T12:03:00+00:00",
            "verified": "yes",
            "online": "yes",
            "target": "Microsoft"
        },
        {
            "phish_id": "100005",
            "url": "http://amazon-prime-card-bonus-promotions.com/claim",
            "phish_detail_url": "https://www.phishtank.com/phish_detail.php?phish_id=100005",
            "submission_time": "2026-06-07T12:04:00+00:00",
            "verified": "yes",
            "online": "yes",
            "target": "Amazon"
        }
    ]
    
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(mock_data, f, indent=2)
        
    print(f"Generated mock PhishTank database JSON file in {target_path} successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch PhishTank verified phishing data.")
    parser.add_argument("--mock", action="store_true", help="Generate small mock datasets locally for offline testing.")
    args = parser.parse_args()
    if args.mock:
        generate_mock()
    else:
        download_phishtank()
