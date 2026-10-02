from app.utils.hashing import calculate_content_hash

def test_hashing_consistency():
    """
    Verifies that identical subject and body values yield the exact same SHA-256 hash.
    """
    subject = "  Meeting update  "
    body = "Hi team, see you tomorrow."
    
    hash1 = calculate_content_hash(subject, body)
    hash2 = calculate_content_hash(subject, body)
    
    assert hash1 == hash2

def test_hashing_variance():
    """
    Verifies that different subject or body values yield different SHA-256 hashes.
    """
    hash_base = calculate_content_hash("Subject A", "Body content")
    hash_diff_subject = calculate_content_hash("Subject B", "Body content")
    hash_diff_body = calculate_content_hash("Subject A", "Different body content")
    
    assert hash_base != hash_diff_subject
    assert hash_base != hash_diff_body
    assert hash_diff_subject != hash_diff_body
