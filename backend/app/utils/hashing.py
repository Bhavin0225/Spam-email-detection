import hashlib

def calculate_content_hash(subject: str, body: str) -> str:
    """
    Generates a unique SHA-256 content hash based on normalized subject and body content.
    Used to detect and drop duplicate records during ingestion and incoming scans.
    """
    subject_normalized = (subject or "").strip()
    body_normalized = (body or "").strip()
    
    # Combined normalized string
    combined = f"{subject_normalized}|{body_normalized}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()
