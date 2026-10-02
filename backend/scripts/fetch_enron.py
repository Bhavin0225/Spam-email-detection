import os
import sys
import tarfile
import urllib.request
import argparse

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "enron")

def download_and_extract():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Mirror URL for standard compact enron1 dataset
    url = "http://www.aueb.gr/users/ion/data/enron-spam/raw/enron1.tar.gz"
    filename = "enron1.tar.gz"
    target_path = os.path.join(DATA_DIR, filename)
    
    print(f"Downloading Enron1 dataset from {url}...")
    try:
        opener = urllib.request.build_opener()
        opener.addheaders = [("User-Agent", "Mozilla/5.0")]
        urllib.request.install_opener(opener)
        
        urllib.request.urlretrieve(url, target_path)
        
        print(f"Extracting {filename} to {DATA_DIR}...")
        with tarfile.open(target_path, "r:gz") as tar:
            tar.extractall(path=DATA_DIR)
            
        os.remove(target_path)
        print("Extracted Enron1 dataset successfully.")
    except Exception as e:
        print(f"ERROR: Failed to fetch {url}: {str(e)}", file=sys.stderr)
        print("Please consider running with --mock to run tests in offline environments.", file=sys.stderr)
        sys.exit(1)

def generate_mock():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Establish sub-folders mirroring expected enron1 extraction layout
    base_dir = os.path.join(DATA_DIR, "enron1")
    ham_dir = os.path.join(base_dir, "ham")
    spam_dir = os.path.join(base_dir, "spam")
    os.makedirs(ham_dir, exist_ok=True)
    os.makedirs(spam_dir, exist_ok=True)
    
    mock_ham = [
        "Subject: enron meeting slides\nFrom: employee@enron.com\n\nAttached are the financial report slides for tomorrow's executive presentation.",
        "Subject: schedule confirmation\nFrom: coordinator@enron.com\n\nPlease confirm your availability for the natural gas trading strategy alignment.",
        "Subject: out of office\nFrom: coworker@enron.com\n\nI will be out of the office starting Thursday. For urgent queries, contact our desk."
    ]
    
    mock_spam = [
        "Subject: home loan rates dropped\nFrom: deals@homeloan-info.com\n\nRefinance today and save thousands on your mortgage. Click here for details.",
        "Subject: investment alerts\nFrom: stockpicks@pennystockalerts.net\n\nThis small tech stock is set to surge next week. Buy shares now before it goes up.",
        "Subject: custom software discounts\nFrom: software@discounted-soft.biz\n\nGet up to 70% off popular operating systems and design suites. Limited quantities."
    ]
    
    for i, content in enumerate(mock_ham):
        with open(os.path.join(ham_dir, f"0000{i}.mock"), "w", encoding="utf-8") as f:
            f.write(content)
            
    for i, content in enumerate(mock_spam):
        with open(os.path.join(spam_dir, f"0000{i}.mock"), "w", encoding="utf-8") as f:
            f.write(content)
            
    print(f"Generated mock Enron1 files in {base_dir} successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Enron public email corpus.")
    parser.add_argument("--mock", action="store_true", help="Generate small mock datasets locally for offline testing.")
    args = parser.parse_args()
    if args.mock:
        generate_mock()
    else:
        download_and_extract()
