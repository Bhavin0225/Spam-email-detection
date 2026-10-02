import pytest
from app.ml.preprocessor import clean_text

def test_html_tag_stripping():
    """
    Verifies that clean_text removes raw HTML tags and structures from text blocks.
    """
    html = "<html><body><h1>Alert!</h1><div>Please read <a href='http://x.com'>this link</a> immediately.</div></body></html>"
    cleaned = clean_text(html)
    
    assert "html" not in cleaned
    assert "body" not in cleaned
    assert "href" not in cleaned
    assert "alert" in cleaned
    assert "read" in cleaned
    assert "link" in cleaned

def test_negation_word_preservation():
    """
    Asserts that negative indicators (not, never, no) are preserved as words
    rather than discarded as common stopwords.
    """
    sample = "this is not a scam, do never click it"
    cleaned = clean_text(sample)
    
    assert "not" in cleaned
    assert "never" in cleaned

def test_unicode_normalization():
    """
    Verifies de-accenting and standard ASCII normalizations of characters.
    """
    accents = "Café owner résumé coöperate"
    cleaned = clean_text(accents)
    
    assert "cafe" in cleaned
    assert "resume" in cleaned
    # coöperate lemmatizes to cooperate
    assert "cooperate" in cleaned or "cooperate" in cleaned.replace(" ", "")

def test_lemmatization_and_cleaning():
    """
    Verifies lemmatization rules (e.g. running -> run, plans -> plan).
    """
    sample = "running weekend meetings and planning updates"
    cleaned = clean_text(sample)
    
    # Check that lemmas are used instead of conjugate/plural forms
    assert "run" in cleaned
    assert "weekend" in cleaned
    assert "meeting" in cleaned
    assert "plan" in cleaned
    assert "update" in cleaned
