"""
Email provider connectors for inbox scanning.
Supports Gmail (OAuth2) and universal IMAP (Outlook, Yahoo, custom).
"""

# Pre-configured IMAP provider settings
IMAP_PROVIDERS = {
    "gmail": {"host": "imap.gmail.com", "port": 993},
    "outlook": {"host": "outlook.office365.com", "port": 993},
    "yahoo": {"host": "imap.mail.yahoo.com", "port": 993},
}
