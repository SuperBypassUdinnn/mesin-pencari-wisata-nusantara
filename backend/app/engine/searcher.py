"""Ranked retrieval engine for the wisata search engine.

Consumes a preprocessed query and an Elasticsearch client and produces ranked
retrieval results across three retrieval models:

- bm25:      Okapi BM25 (k1=1.2, b=0.75) over wisata_custom, match/multi-match
             on title and content_preprocessed.
- lm_dirichlet: Language model with Dirichlet smoothing (mu=2000) over
             wisata_custom, where the custom_lm_dirichlet similarity is
             configured in the index settings.
- baseline:  Standard BM25 over wisata_baseline, match/multi-match on raw
             title and content using the standard analyzer.

Provides search_documents() which handles query preprocessing for
wisata_custom, server latency measurement in milliseconds, hit formatting with
rank, score, title, snippet, metadata badges, and URL, plus snippet fallback
to the raw content when Elasticsearch returns no highlight.
"""

from __future__ import annotations

import time
from typing import Dict, List

from backend.app.engine.preprocessor import preprocess_text

# ---------------------------------------------------------------------------
# Index names (shared with the indexer module)
# ---------------------------------------------------------------------------

INDEX_CUSTOM = "wisata_custom"
INDEX_BASELINE = "wisata_baseline"

# ---------------------------------------------------------------------------
# Retrieval model identifiers
# ---------------------------------------------------------------------------

MODEL_BM25 = "bm25"
MODEL_LM_DIRICHLET = "lm_dirichlet"
MODEL_BASELINE = "baseline"

_CUSTOM_MODELS = {MODEL_BM25, MODEL_LM_DIRICHLET}

# ---------------------------------------------------------------------------
# Highlighting configuration
# ---------------------------------------------------------------------------

HIGHLIGHT_PRE_TAG = "<em>"
HIGHLIGHT_POST_TAG = "</em>"

# Fallback snippet length (characters) used when no highlight is returned.
SNIPPET_FALLBACK_CHARS = 200


def _index_for_model(model: str) -> str:
    """Resolve the target Elasticsearch index for a retrieval model."""
    normalized = model.lower()
    if normalized in _CUSTOM_MODELS:
        return INDEX_CUSTOM
    if normalized == MODEL_BASELINE:
        return INDEX_BASELINE
    raise ValueError(f"Unsupported retrieval model: {model}")


def _highlight_config(fields: List[str]) -> dict:
    """Build the Elasticsearch highlight block using <em> emphasis tags."""
    return {
        "pre_tags": [HIGHLIGHT_PRE_TAG],
        "post_tags": [HIGHLIGHT_POST_TAG],
        "fields": {field: {} for field in fields},
    }


def build_search_query(query_text: str, model: str, top_k: int = 10) -> dict:
    """Build an Elasticsearch search request for a retrieval model.

    Returns a dict with "index" (target index name) and "body" (request body
    suitable for es_client.search(index=..., body=...)).

    For bm25 and lm_dirichlet the query runs on wisata_custom against
    title and content_preprocessed. For baseline the query runs on
    wisata_baseline against raw title and content.
    """
    index_name = _index_for_model(model)

    if index_name == INDEX_CUSTOM:
        search_fields = ["title", "content_preprocessed"]
    else:
        search_fields = ["title", "content"]

    body = {
        "query": {
            "multi_match": {
                "query": query_text,
                "fields": search_fields,
            }
        },
        "size": top_k,
        "highlight": _highlight_config(search_fields),
    }

    return {"index": index_name, "body": body}


def _extract_hits(response: dict) -> List[dict]:
    """Extract the hit list from an Elasticsearch search response."""
    if not isinstance(response, dict):
        return []
    hits_wrapper = response.get("hits", {})
    if not isinstance(hits_wrapper, dict):
        return []
    hits = hits_wrapper.get("hits", [])
    return hits if isinstance(hits, list) else []


def _total_hits(response: dict) -> int:
    """Read the total hit count, tolerant of ES 7.x dict and ES 8.x int forms."""
    if not isinstance(response, dict):
        return 0
    hits_wrapper = response.get("hits", {})
    if not isinstance(hits_wrapper, dict):
        return 0
    total = hits_wrapper.get("total", 0)
    if isinstance(total, dict):
        return int(total.get("value", 0) or 0)
    return int(total or 0)


def _extract_snippet(highlight: dict, source: dict) -> str:
    """Return the first highlighted fragment, falling back to raw content."""
    if isinstance(highlight, dict):
        for fragments in highlight.values():
            if isinstance(fragments, list) and fragments:
                return str(fragments[0])
    content = source.get("content") or source.get("content_preprocessed", "")
    if content:
        return str(content)[:SNIPPET_FALLBACK_CHARS]
    return ""


def format_search_hit(hit: dict, rank: int) -> dict:
    """Format a single Elasticsearch hit into a ranked result dict.

    Keys: rank, score, title, snippet, url, badges (source, location,
    category). The snippet comes from the highlight fragment when available,
    otherwise from a fallback slice of the document content.
    """
    if not isinstance(hit, dict):
        hit = {}
    source = hit.get("_source", {})
    if not isinstance(source, dict):
        source = {}
    highlight = hit.get("highlight", {})
    if not isinstance(highlight, dict):
        highlight = {}

    return {
        "rank": rank,
        "score": hit.get("_score"),
        "title": source.get("title", ""),
        "snippet": _extract_snippet(highlight, source),
        "url": source.get("url", ""),
        "badges": {
            "source": source.get("source", ""),
            "location": source.get("location", ""),
            "category": source.get("category", ""),
        },
    }


def search_documents(
    es_client,
    query: str,
    model: str,
    top_k: int = 10,
    preprocessed: bool = True,
) -> dict:
    """Execute a search and return ranked results with latency.

    For wisata_custom targets the incoming query is preprocessed with
    preprocess_text() before being sent to Elasticsearch (when preprocessed is
    True). Server execution latency is measured in milliseconds around the
    es_client.search() call, so the method works with both real and mock
    clients in unit tests.

    Returns a dict with query, model, index, top_k, latency_ms, total, and
    results (list of formatted hit dicts).
    """
    index_name = _index_for_model(model)

    effective_query = query
    if index_name == INDEX_CUSTOM and preprocessed:
        effective_query = preprocess_text(query)

    request = build_search_query(effective_query, model, top_k=top_k)
    body = request["body"]

    start_time = time.perf_counter()
    response = es_client.search(index=index_name, body=body)
    latency_ms = (time.perf_counter() - start_time) * 1000.0

    hits = _extract_hits(response)
    total = _total_hits(response)
    results = [
        format_search_hit(hit, rank=position + 1)
        for position, hit in enumerate(hits)
    ]

    return {
        "query": query,
        "model": model,
        "index": index_name,
        "top_k": top_k,
        "latency_ms": round(latency_ms, 4),
        "total": total,
        "results": results,
    }
