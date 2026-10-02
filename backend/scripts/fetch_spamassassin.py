import os
import sys
import tarfile
import urllib.request
import argparse

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "spamassassin")

def download_and_extract():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    urls = [
        "https://spamassassin.apache.org/old/publiccorpus/20030228_easy_ham.tar.bz2",
        "https://spamassassin.apache.org/old/publiccorpus/20030228_spam.tar.bz2"
    ]
    
    for url in urls:
        filename = url.split("/")[-1]
        target_path = os.path.join(DATA_DIR, filename)
        
        print(f"Downloading {url}...")
        try:
            # Simple agent header to avoid server blocks
            opener = urllib.request.build_opener()
            opener.addheaders = [("User-Agent", "Mozilla/5.0")]
            urllib.request.install_opener(opener)
            
            urllib.request.urlretrieve(url, target_path)
            
            print(f"Extracting {filename} to {DATA_DIR}...")
            with tarfile.open(target_path, "r:bz2") as tar:
                tar.extractall(path=DATA_DIR)
                
            os.remove(target_path)
            print(f"Extracted {filename} successfully.")
        except Exception as e:
            print(f"ERROR: Failed to fetch {url}: {str(e)}", file=sys.stderr)
            print("Please consider running with --mock to run tests in offline environments.", file=sys.stderr)
            sys.exit(1)

def generate_mock():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Create sub-folders mirroring tar extraction structures
    ham_dir = os.path.join(DATA_DIR, "easy_ham")
    spam_dir = os.path.join(DATA_DIR, "spam")
    os.makedirs(ham_dir, exist_ok=True)
    os.makedirs(spam_dir, exist_ok=True)
    
    mock_ham_emails = [
        "Subject: Project Update Meeting\nFrom: manager@workplace.com\n\nHi team, we will meet at 10 AM to discuss Phase 3 tasks. Please bring your updates.",
        "Subject: Weekend Plans?\nFrom: friend@personal.org\n\nHi there, let's catch up on Saturday afternoon for coffee at the central cafe.",
        "Subject: Lunch Options today\nFrom: coworker@office.com\n\nAre we ordering pizza or going out for burgers? Let me know by noon so we can organize."
    ]
    
    mock_spam_emails = [
        "Subject: URGENT: Claim your $1000 prize now!\nFrom: reward@spam-central.net\n\nCongratulations! You have been selected to win. Click http://scam-site.net/login to verify your account details.",
        "Subject: Double your income in 24 hours!\nFrom: guru@cryptosecure.co\n\nInvest $100 in our new tokens and double your wealth. Register here immediately: http://doubler.com",
        "Subject: Purchase medications online cheap\nFrom: pills@cheap-meds-pharmacy.com\n\nBuy medical products online with no prescription needed. Free shipping on all international orders."
    ]
    
    for i, content in enumerate(mock_ham_emails):
        with open(os.path.join(ham_dir, f"0000{i}.mock"), "w", encoding="utf-8") as f:
            f.write(content)
            
    for i, content in enumerate(mock_spam_emails):
        with open(os.path.join(spam_dir, f"0000{i}.mock"), "w", encoding="utf-8") as f:
            f.write(content)
            
    print(f"Generated mock SpamAssassin corpus files in {DATA_DIR} successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch SpamAssassin public email corpus.")
    parser.add_argument("--mock", action="store_true", help="Generate small mock datasets locally for offline testing.")
    args = parser.parse_args()
    if args.mock:
        generate_mock()
    else:
        download_and_extract()
