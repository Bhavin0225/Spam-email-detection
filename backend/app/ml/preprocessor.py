import re
import unicodedata
import spacy
import spacy.cli
from bs4 import BeautifulSoup
from app.utils.logger import logger

_nlp = None

def get_nlp():
    """
    Retrieves the spaCy language model. Auto-downloads 'en_core_web_sm' from spaCy's CDN
    if it is missing in the current Python environment.
    """
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.info("spaCy 'en_core_web_sm' model not found. Downloading dynamically...")
            try:
                spacy.cli.download("en_core_web_sm")
                _nlp = spacy.load("en_core_web_sm")
            except Exception as e:
                logger.critical(f"Failed to dynamically download spaCy model: {str(e)}")
                raise RuntimeError(f"spaCy model download failed: {str(e)}") from e
    return _nlp

# Preserved negation terms that must not be removed by the stopword filters
NEGATION_WORDS = {"not", "no", "never", "none", "neither", "nor", "but", "against"}

def clean_text(text: str) -> str:
    """
    Processes raw text or HTML through the cleaning pipeline:
    1. Strips HTML tags using BeautifulSoup.
    2. Normalizes accented characters to ASCII equivalents.
    3. Lowers text casing.
    4. Tokenizes, filters out non-negation stopwords, and lemmatizes tokens via spaCy.
    """
    if not text:
        return ""

    # 1. HTML tag removal
    try:
        # Strip HTML markup using html.parser
        soup = BeautifulSoup(text, "html.parser")
        text = soup.get_text(separator=" ")
    except Exception as e:
        logger.warning(f"BeautifulSoup clean failed. Falling back to regex parsing: {str(e)}")
        # Regex fallback to strip tags
        text = re.sub(r"<[^>]+>", " ", text)

    # 2. Unicode normalization (removes accent marks and maps to ASCII)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")

    # 3. Normalization (lowercasing and whitespace cleanup)
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()

    # 4. Tokenization, stopword cleaning, and Lemmatization
    nlp = get_nlp()
    doc = nlp(text)

    cleaned_tokens = []
    for token in doc:
        # Skip punctuation, standalone numbers, symbols and spaces
        if token.is_punct or token.is_space or token.like_num or token.pos_ in ("SYM", "PUNCT"):
            continue

        # Stopword filtration (negation preservation logic)
        is_stopword = token.is_stop and (token.text not in NEGATION_WORDS)
        if not is_stopword:
            lemma = token.lemma_.strip()
            # Retain non-empty lemmas
            if lemma:
                cleaned_tokens.append(lemma)

    return " ".join(cleaned_tokens)
