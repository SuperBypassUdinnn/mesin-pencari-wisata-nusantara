"""Custom travel-domain preprocessing pipeline for Indonesian tourism text.

Consumes raw text strings from crawled documents or incoming search queries
and produces space-delimited stemmed tokens, plus a structured inspection
report for GUI side-by-side comparison and evidence tables.

Pipeline stages:
    1. Case folding (lowercasing)
    2. HTML tag stripping
    3. Emoji / pictograph removal
    4. Ticket price sanitization (e.g. "Rp 15.000,-")
    5. Operational hours removal (e.g. "08.00-17.00 WIB")
    6. Non-alphanumeric character cleanup
    7. Whitespace tokenization
    8. Travel stopword filtering with tourism-domain whitelist
    9. PySastrawi Indonesian morphological stemming

The Sastrawi StemmerFactory is instantiated once as a module-level singleton
to avoid repeated factory construction overhead across calls.
"""

from __future__ import annotations

import re
from typing import Dict, List

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import (
    StopWordRemoverFactory as StopwordFactory,
)

# ---------------------------------------------------------------------------
# Singleton stemmer factory and stemmer (created once at import time)
# ---------------------------------------------------------------------------

_STEMMER_FACTORY = StemmerFactory()
STEMMER = _STEMMER_FACTORY.create_stemmer()

# ---------------------------------------------------------------------------
# Stopword set: Sastrawi Indonesian stopwords merged with travel blog noise
# ---------------------------------------------------------------------------

_STOPWORD_FACTORY = StopwordFactory()
SASTRAWI_STOPWORDS = set(_STOPWORD_FACTORY.get_stop_words())

TRAVEL_NOISE_STOPWORDS = {
    "baca",
    "klik",
    "sumber",
    "foto",
    "artikel",
    "penulis",
    "instagram",
    "detik",
    "kompas",
    "wisatawan",
    "berkunjung",
    "lokasi",
    "berada",
    "terletak",
}

STOPWORDS = SASTRAWI_STOPWORDS | TRAVEL_NOISE_STOPWORDS

# ---------------------------------------------------------------------------
# Tourism-domain whitelist: core terms preserved verbatim (never stoplisted,
# never stemmed) so destination and facility keywords survive preprocessing
# ---------------------------------------------------------------------------

WHITELIST = {
    "pantai",
    "curug",
    "candi",
    "danau",
    "puncak",
    "goa",
    "hutan",
    "taman",
    "rute",
    "tiket",
    "pulau",
    "air",
    "terjun",
    "gunung",
    "desa",
    "wisata",
}

# ---------------------------------------------------------------------------
# Compiled cleaning regex patterns
# ---------------------------------------------------------------------------

HTML_PATTERN = re.compile(r"<[^>]+>")

EMOJI_PATTERN = re.compile(
    r"[\U0001F600-\U0001F64F"  # emoticons
    r"\U0001F300-\U0001F5FF"  # miscellaneous symbols and pictographs
    r"\U0001F680-\U0001F6FF"  # transport and map symbols
    r"\U0001F1E0-\U0001F1FF"  # regional indicator symbols
    r"\U00002700-\U000027BF"  # dingbats
    r"\U00002600-\U000026FF"  # miscellaneous symbols
    r"\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
    r"\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
    r"\u200d"  # zero-width joiner
    r"\ufe0f"  # variation selector-16
    r"]+",
    re.UNICODE,
)

PRICE_PATTERN = re.compile(r"rp\s*[\d\.,]+\s*-?\s*", re.IGNORECASE)
STANDALONE_PRICE_PATTERN = re.compile(r"\b\d{1,3}(?:\.\d{3})+(?:\s*,\s*)?\b")

HOURS_PATTERN = re.compile(
    r"\b\d{1,2}[:.\-]\d{2}\s*(?:[-–]\s*\d{1,2}[:.\-]\d{2})?\s*(?:wib|wita|wit)\b",
    re.IGNORECASE,
)

NON_ALPHANUMERIC_PATTERN = re.compile(r"[^a-z0-9\s]+")
WHITESPACE_PATTERN = re.compile(r"\s+")


def _clean(text: str) -> str:
    """Run case folding and all cleaning regexes over raw input text."""
    case_folded = text.lower()
    no_html = HTML_PATTERN.sub(" ", case_folded)
    no_emoji = EMOJI_PATTERN.sub(" ", no_html)
    no_price = PRICE_PATTERN.sub(" ", no_emoji)
    no_price = STANDALONE_PRICE_PATTERN.sub(" ", no_price)
    no_hours = HOURS_PATTERN.sub(" ", no_price)
    no_symbols = NON_ALPHANUMERIC_PATTERN.sub(" ", no_hours)
    collapsed = WHITESPACE_PATTERN.sub(" ", no_symbols).strip()
    return collapsed


def preprocess_text(text: str) -> str:
    """Preprocess raw Indonesian tourism text into space-delimited stemmed tokens.

    Stages: case folding, cleaning regexes, tokenization, travel stopword
    filtering (whitelist-aware), and PySastrawi stemming.
    """
    tokens = _clean(text).split()
    filtered = [
        token for token in tokens if token not in STOPWORDS or token in WHITELIST
    ]
    stemmed = [
        token if token in WHITELIST else STEMMER.stem(token) for token in filtered
    ]
    return " ".join(stemmed)


def inspect_preprocessing(text: str) -> Dict[str, object]:
    """Return step-by-step token streams for GUI inspector and report tables.

    Keys:
        raw:          original input text
        case_folded:  text after lowercasing
        cleaned:      text after all regex cleaning and whitespace collapse
        tokens:       whitespace tokens after cleaning
        filtered:     tokens after travel stopword filtering (whitelist kept)
        stemmed:      final PySastrawi stemmed tokens (whitelist kept verbatim)
    """
    case_folded = text.lower()
    no_html = HTML_PATTERN.sub(" ", case_folded)
    no_emoji = EMOJI_PATTERN.sub(" ", no_html)
    no_price = PRICE_PATTERN.sub(" ", no_emoji)
    no_price = STANDALONE_PRICE_PATTERN.sub(" ", no_price)
    no_hours = HOURS_PATTERN.sub(" ", no_price)
    no_symbols = NON_ALPHANUMERIC_PATTERN.sub(" ", no_hours)
    cleaned = WHITESPACE_PATTERN.sub(" ", no_symbols).strip()

    tokens = cleaned.split()
    filtered = [
        token for token in tokens if token not in STOPWORDS or token in WHITELIST
    ]
    stemmed = [
        token if token in WHITELIST else STEMMER.stem(token) for token in filtered
    ]

    return {
        "raw": text,
        "case_folded": case_folded,
        "cleaned": cleaned,
        "tokens": tokens,
        "filtered": filtered,
        "stemmed": stemmed,
    }
