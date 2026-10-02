import os
import re
import sys
import json
import uuid
import email
from email.policy import default
from datetime import datetime, timezone
import pandas as pd
from app.database.connection import db_manager
from app.database.collections import get_collection
from app.utils.hashing import calculate_content_hash
from app.utils.logger import logger

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def parse_email_text(raw_text: str) -> dict:
    """
    Parses a raw email string into structured attributes: subject, sender, body, domains, links.
    Handles multipart parsing, headers extraction, and plain text fallbacks.
    """
    try:
        msg = email.message_from_string(raw_text, policy=default)
        subject = msg.get("Subject", "") or ""
        sender = msg.get("From", "") or ""
        
        # Normalize sender domain
        sender_domain = ""
        if sender and "@" in sender:
            # Extract domain from email (e.g. "User <user@domain.com>" -> "domain.com")
            match = re.search(r"@([\w.-]+)", sender)
            if match:
                sender_domain = match.group(1).lower().strip()

        # Extract email body
        body = ""
        if msg.is_multipart():
            # Walk multipart sections
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body = part.get_content()
                    break
                elif content_type == "text/html" and not body:
                    body = part.get_content()
        else:
            # Single-part payload
            try:
                body = msg.get_content()
            except Exception:
                body = msg.get_payload()

        if not isinstance(body, str):
            body = str(body or "")

        # Extract URLs
        links = re.findall(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", body)

        # Get all Received headers to compute hop count
        received_headers = msg.get_all("Received") or []
        hop_count = len(received_headers)

        # Gather custom security validation headers
        headers = {
            "spf": msg.get("Received-SPF", "") or "",
            "dkim": msg.get("DKIM-Signature", "") or "",
            "dmarc": msg.get("Authentication-Results", "") or "",
            "reply-to": msg.get("Reply-To", "") or "",
            "hop_count": hop_count
        }
        
        return {
            "subject": subject,
            "sender": sender,
            "sender_domain": sender_domain,
            "body_text": body,
            "links": links,
            "headers": headers
        }
    except Exception as e:
        logger.error(f"Email parsing exception: {str(e)}")
        return {
            "subject": "",
            "sender": "",
            "sender_domain": "",
            "body_text": raw_text,
            "links": [],
            "headers": {
                "spf": "",
                "dkim": "",
                "dmarc": "",
                "reply-to": "",
                "hop_count": 0
            }
        }

def read_files_from_dir(path: str) -> list:
    """
    Lists and reads raw text files from target directory.
    """
    files_data = []
    if not os.path.exists(path):
        logger.warning(f"Data directory does not exist: {path}")
        return files_data

    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        if os.path.isdir(filepath):
            continue
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                files_data.append(content)
        except Exception as e:
            logger.error(f"Failed to read file {filepath}: {str(e)}")
    return files_data

def process_source_files(source_name: str, ham_path: str, spam_path: str) -> list:
    """
    Loads raw text files, parses them, and tags them with classification labels.
    """
    records = []
    
    # Process ham entries
    logger.info(f"Loading {source_name} ham records...")
    ham_emails = read_files_from_dir(ham_path)
    for raw_email in ham_emails:
        parsed = parse_email_text(raw_email)
        parsed["dataset_source"] = source_name
        parsed["label"] = 0  # Ham / legitimate
        records.append(parsed)
        
    # Process spam entries
    logger.info(f"Loading {source_name} spam records...")
    spam_emails = read_files_from_dir(spam_path)
    for raw_email in spam_emails:
        parsed = parse_email_text(raw_email)
        parsed["dataset_source"] = source_name
        parsed["label"] = 1  # Spam / suspicious
        records.append(parsed)

    return records

def process_phishtank_file(json_path: str) -> list:
    """
    Reads PhishTank active entries JSON and generates email wrapper documents.
    """
    records = []
    if not os.path.exists(json_path):
        logger.warning(f"PhishTank data feed not found at {json_path}")
        return records
        
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            phish_list = json.load(f)
            
        # Ingest up to 1000 items to balance training dataset distributions
        target_count = min(len(phish_list), 1000)
        logger.info(f"Loading {target_count} PhishTank verified phishing entries...")
        
        for item in phish_list[:target_count]:
            target_brand = item.get("target", "Unknown Brand")
            phish_url = item.get("url", "")
            
            # Wrap url details inside custom phishing alert email envelope
            subject = f"Security Notice: Verify your access account at {target_brand}"
            body_text = f"Dear User, verify your login credentials immediately to prevent account suspension: {phish_url}"
            
            records.append({
                "subject": subject,
                "sender": "alerts@phishtank.com",
                "sender_domain": "phishtank.com",
                "body_text": body_text,
                "links": [phish_url],
                "headers": {
                    "spf": "",
                    "dkim": "",
                    "dmarc": "",
                    "reply-to": "",
                    "hop_count": 0
                },
                "dataset_source": "PhishTank",
                "label": 1  # Suspicious
            })
    except Exception as e:
        logger.error(f"PhishTank JSON parse failed: {str(e)}")
        
    return records

def compute_dataset_splits(records: list) -> list:
    """
    Splits records into 70% Train, 15% Validation, and 15% Test.
    """
    if not records:
        return []
        
    # Convert to pandas DataFrame for quick indexing and shuffling
    df = pd.DataFrame(records)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    n = len(df)
    train_idx = int(n * 0.70)
    val_idx = int(n * 0.85)
    
    splits = []
    for idx, row in df.iterrows():
        record = row.to_dict()
        if idx < train_idx:
            record["split"] = "train"
        elif idx < val_idx:
            record["split"] = "validation"
        else:
            record["split"] = "test"
        splits.append(record)
        
    return splits

def ingest_pipeline():
    # Connect to MongoDB
    logger.info("Initializing database connection for ingestion...")
    db_manager.connect()
    
    emails_collection = get_collection("emails")
    metadata_collection = get_collection("dataset_metadata")
    
    raw_records = []
    
    # 1. Load and parse SpamAssassin
    sa_ham = os.path.join(DATA_DIR, "spamassassin", "easy_ham")
    sa_spam = os.path.join(DATA_DIR, "spamassassin", "spam")
    raw_records.extend(process_source_files("SpamAssassin", sa_ham, sa_spam))
    
    # 2. Load and parse Enron
    en_ham = os.path.join(DATA_DIR, "enron", "enron1", "ham")
    en_spam = os.path.join(DATA_DIR, "enron", "enron1", "spam")
    raw_records.extend(process_source_files("Enron", en_ham, en_spam))
    
    # 3. Load and parse PhishTank
    pt_json = os.path.join(DATA_DIR, "phishtank", "online-valid.json")
    raw_records.extend(process_phishtank_file(pt_json))
    
    if not raw_records:
        logger.warning("No email records loaded. Ingestion process completed with 0 imports.")
        return
        
    logger.info(f"Loaded total of {len(raw_records)} records. Applying split and deduplication...")
    
    # Compute content hashes and filter out duplicates matching database collection
    deduplicated = []
    duplicate_count = 0
    seen_hashes = set()
    
    for r in raw_records:
        content_hash = calculate_content_hash(r["subject"], r["body_text"])
        
        # Check against local buffer duplicate
        if content_hash in seen_hashes:
            duplicate_count += 1
            continue
            
        # Check against MongoDB collection duplicate
        existing = emails_collection.find_one({"content_hash": content_hash})
        if existing:
            duplicate_count += 1
            continue
            
        seen_hashes.add(content_hash)
        r["content_hash"] = content_hash
        r["email_id"] = str(uuid.uuid4())
        r["created_at"] = datetime.now(timezone.utc)
        deduplicated.append(r)
        
    logger.info(f"Filtered out {duplicate_count} duplicates. {len(deduplicated)} new records to insert.")
    
    # Sort into train/validation/test splits by source for even distribution
    final_records = []
    sources = set(r["dataset_source"] for r in deduplicated)
    
    for src in sources:
        src_records = [r for r in deduplicated if r["dataset_source"] == src]
        split_records = compute_dataset_splits(src_records)
        final_records.extend(split_records)
        
    if not final_records:
        logger.info("No new unique records found. Ingestion skipped.")
        return

    # Bulk insert records
    logger.info("Batch inserting records to emails collection...")
    emails_collection.insert_many(final_records)
    
    # Create dataset metadata registries
    logger.info("Writing ingestion metadata records...")
    for src in sources:
        src_subset = [r for r in final_records if r["dataset_source"] == src]
        total = len(src_subset)
        spam = sum(1 for r in src_subset if r["label"] == 1)
        ham = total - spam
        
        metadata_doc = {
            "dataset_id": str(uuid.uuid4()),
            "name": f"{src} Ingestion Dataset",
            "source": src,
            "version": "1.0.0",
            "record_count": total,
            "spam_count": spam,
            "ham_count": ham,
            "ingestion_date": datetime.now(timezone.utc),
            "split_ratios": {"train": 0.70, "validation": 0.15, "test": 0.15},
            "checksum": calculate_content_hash(src, str(total))
        }
        metadata_collection.insert_one(metadata_doc)
        
    logger.info("Ingestion pipeline execution completed successfully.")

if __name__ == "__main__":
    ingest_pipeline()
