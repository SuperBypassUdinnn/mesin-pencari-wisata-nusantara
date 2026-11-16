"""Synonym-based query expansion for Indonesian tourism search.

Consumes a raw user query and produces an expanded query by appending
domain synonyms from a curated bidirectional Indonesian tourism
dictionary. Returns the original query, the expanded query, a flag
indicating whether any expansion occurred, and the list of added
synonyms.

The dictionary is intentionally curated (not scraped) so that each
synonym pair is verified for tourism-domain correctness in Indonesian.
"""

from __future__ import annotations

import re
from typing import Dict, List

# ---------------------------------------------------------------------------
# Curated bidirectional Indonesian tourism synonym dictionary
# Each key maps to a list of synonyms; every pair is represented in both
# directions so lookup works regardless of which term appears in a query.
# ---------------------------------------------------------------------------

_SYNONYM_DICTIONARY: Dict[str, List[str]] = {
    "curug": ["air terjun"],
    "air terjun": ["curug"],
    "pelesir": ["wisata", "pariwisata"],
    "wisata": ["pelesir", "pariwisata"],
    "pariwisata": ["wisata", "pelesir"],
    "penginapan": ["hotel", "losmen", "villa"],
    "hotel": ["penginapan", "losmen", "villa"],
    "losmen": ["penginapan", "hotel", "villa"],
    "villa": ["penginapan", "hotel", "losmen"],
    "bahari": ["pantai", "laut"],
    "pantai": ["bahari", "laut", "tepi laut"],
    "laut": ["bahari", "pantai", "tepi laut"],
    "tepi laut": ["pantai", "laut"],
    "snorkeling": ["selam", "menyelam"],
    "selam": ["snorkeling", "menyelam"],
    "menyelam": ["snorkeling", "selam"],
    "candi": ["situs bersejarah", "peninggalan sejarah"],
    "situs bersejarah": ["candi", "peninggalan sejarah"],
    "peninggalan sejarah": ["candi", "situs bersejarah"],
    "gunung": ["puncak", "pegunungan"],
    "puncak": ["gunung", "pegunungan"],
    "pegunungan": ["gunung", "puncak"],
    "danau": ["telaga", "kolam danau"],
    "telaga": ["danau", "kolam danau"],
    "kolam danau": ["danau", "telaga"],
    "goa": ["gua", "guha"],
    "gua": ["goa", "guha"],
    "guha": ["goa", "gua"],
    "taman": ["taman wisata", "taman nasional"],
    "taman wisata": ["taman", "taman nasional"],
    "taman nasional": ["taman", "taman wisata"],
    "pulau": ["nusa", "selat"],
    "nusa": ["pulau", "selat"],
    "selat": ["pulau", "nusa"],
    "desa": ["kampung", "desa wisata"],
    "kampung": ["desa", "desa wisata"],
    "desa wisata": ["desa", "kampung"],
    "tiket": ["entree", "tiket masuk"],
    "entree": ["tiket", "tiket masuk"],
    "tiket masuk": ["tiket", "entree"],
    "rute": ["jalur", "lintasan"],
    "jalur": ["rute", "lintasan"],
    "lintasan": ["rute", "jalur"],
}

_TOKEN_SPLIT_PATTERN = re.compile(r"\s+")


def get_synonym_dictionary() -> Dict[str, List[str]]:
    """Return the curated bidirectional Indonesian tourism synonym dictionary.

    Returns a dict mapping each tourism term to a list of its synonyms.
    Every synonym pair is stored in both directions.
    """
    return dict(_SYNONYM_DICTIONARY)


def _normalize_term(term: str) -> str:
    """Lowercase and collapse whitespace for dictionary lookup."""
    return re.sub(r"\s+", " ", term.strip().lower())


def expand_query(query: str) -> dict:
    """Expand an Indonesian tourism query with dictionary synonyms.

    Splits the query into whitespace-delimited terms (including multi-word
    dictionary entries), detects matching dictionary terms, appends their
    synonyms without duplicating terms already present, and returns a dict
    with keys:

        original:        the input query string
        expanded:        the query with synonyms appended
        has_expansion:   True if any synonym was added
        added_synonyms:  list of synonym strings appended to the query
    """
    original = query
    normalized = _normalize_term(query)
    tokens = normalized.split()

    # Build a set of terms already present (including multi-word forms found
    # as substrings) so we do not re-add synonyms already in the query.
    present = set(tokens)

    added_synonyms: List[str] = []
    seen_added = set()

    # Check single tokens first, then longer dictionary keys that may appear
    # as contiguous multi-word phrases in the query.
    dictionary_keys = sorted(_SYNONYM_DICTIONARY.keys(), key=len, reverse=True)

    for key in dictionary_keys:
        key_tokens = key.split()
        key_len = len(key_tokens)
        if key_len == 0:
            continue
        # Scan the token stream for this multi-word key as a contiguous span.
        for i in range(0, len(tokens) - key_len + 1):
            span = " ".join(tokens[i : i + key_len])
            if span == key:
                for syn in _SYNONYM_DICTIONARY[key]:
                    syn_norm = _normalize_term(syn)
                    if syn_norm not in present and syn_norm not in seen_added:
                        added_synonyms.append(syn_norm)
                        seen_added.add(syn_norm)
                        present.add(syn_norm)
                break

    if added_synonyms:
        expanded = normalized + " " + " ".join(added_synonyms)
    else:
        expanded = normalized

    return {
        "original": original,
        "expanded": expanded,
        "has_expansion": len(added_synonyms) > 0,
        "added_synonyms": added_synonyms,
    }
