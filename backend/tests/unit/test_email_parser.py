from scripts.ingest_data import parse_email_text

def test_parse_email_standard_headers_and_body():
    """
    Verifies decoding of standard headers, domains, Received-SPF and DKIM-Signature tags,
    and link regex resolutions on standard text bodies.
    """
    raw_email = (
        "Subject: Urgent: Renew your billing details\n"
        "From: renewals@netflix-billing.com\n"
        "Reply-To: badguy@scam-reply.com\n"
        "Received: from mail.netflix-billing.com (192.168.1.5)\n"
        "Received: from gateway.com (192.168.1.1)\n"
        "Received-SPF: pass (google.com: domain of renewals@netflix-billing.com)\n"
        "DKIM-Signature: v=1; a=rsa-sha256; d=netflix-billing.com;\n"
        "\n"
        "Hi, please update your billing details at http://netflix-scam.net/renew immediately."
    )
    
    parsed = parse_email_text(raw_email)
    
    assert parsed["subject"] == "Urgent: Renew your billing details"
    assert parsed["sender"] == "renewals@netflix-billing.com"
    assert parsed["sender_domain"] == "netflix-billing.com"
    assert "update your billing details" in parsed["body_text"]
    assert parsed["links"] == ["http://netflix-scam.net/renew"]
    assert "pass" in parsed["headers"]["spf"]
    assert "v=1;" in parsed["headers"]["dkim"]
    assert parsed["headers"]["reply-to"] == "badguy@scam-reply.com"
    assert parsed["headers"]["hop_count"] == 2

def test_parse_email_missing_headers_and_fields():
    """
    Verifies that missing headers or email attributes resolve to empty fields or empty defaults
    and do not throw parse runtime errors.
    """
    raw_email = "\nJust a plain email body text with no headers whatsoever. See www.google.com for info."
    parsed = parse_email_text(raw_email)
    
    assert parsed["subject"] == ""
    assert parsed["sender"] == ""
    assert parsed["sender_domain"] == ""
    assert "plain email body" in parsed["body_text"]
    assert parsed["links"] == ["www.google.com"]
    assert parsed["headers"] == {"spf": "", "dkim": "", "dmarc": "", "reply-to": "", "hop_count": 0}
