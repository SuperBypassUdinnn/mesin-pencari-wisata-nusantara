"""Rocchio relevance feedback for the wisata search engine.

Implements the Rocchio algorithm for query reformulation based on
relevant and non-relevant document feedback, integrated with Elasticsearch
`_termvectors` to read normalized term-frequency vectors.

The revised query vector is computed as::

    Q' = alpha * Q + beta * (1/|Dr|) * sum(D in Dr) - gamma * (1/|Dnr|) * sum(D in Dnr)

Positive-weighted terms are then synthesized into a boosted Elasticsearch
`bool` query for retrieval.
"""

from __future__ import annotations

from typing import Dict, List

from elasticsearch import Elasticsearch


def _resolve_termvectors_client(es_client):
    """Resolve the termvectors method across elasticsearch client versions.

    elasticsearch 8.x exposes both `termvectors` and `term_vectors`, while
    older 7.x clients expose `termvectors`. Return whichever attribute
    exists so this helper remains resilient across client variations.
    """
    return getattr(es_client, "termvectors", None) or getattr(es_client, "term_vectors", None)


def calculate_rocchio_weights(
    query_vec: Dict[str, float],
    rel_vecs: List[Dict[str, float]],
    non_rel_vecs: List[Dict[str, float]],
    alpha: float = 1.0,
    beta: float = 0.75,
    gamma: float = 0.15,
) -> Dict[str, float]:
    """Compute the Rocchio revised query vector.

    Returns a dict mapping each term to its adjusted weight. Terms whose
    final weight drops to zero or below are retained with their signed
    value so callers can decide whether to filter or clamp them.
    """
    weights: Dict[str, float] = {}

    # alpha * Q
    for term, value in query_vec.items():
        weights[term] = weights.get(term, 0.0) + alpha * value

    # beta * (1/|Dr|) * sum(D in Dr)
    if rel_vecs:
        rel_count = len(rel_vecs)
        for vec in rel_vecs:
            for term, value in vec.items():
                weights[term] = weights.get(term, 0.0) + (beta / rel_count) * value

    # - gamma * (1/|Dnr|) * sum(D in Dnr)
    if non_rel_vecs:
        non_rel_count = len(non_rel_vecs)
        for vec in non_rel_vecs:
            for term, value in vec.items():
                weights[term] = weights.get(term, 0.0) - (gamma / non_rel_count) * value

    return weights


def fetch_term_vectors(
    es_client: Elasticsearch, index_name: str, doc_ids: List[str]
) -> List[dict]:
    """Read normalized TF-IDF term vectors for a list of document IDs.

    Uses the resilient `_resolve_termvectors_client` helper so the call works
    across elasticsearch client versions. Returns a list of dicts, each with
    `doc_id` and `vector` (term -> term_freq) keys. Documents that return no
    term vectors yield an empty vector dict.
    """
    termvectors_fn = _resolve_termvectors_client(es_client)
    if termvectors_fn is None:
        raise AttributeError(
            "elasticsearch client exposes neither 'termvectors' nor 'term_vectors'"
        )

    results: List[dict] = []
    field = "content_preprocessed" if index_name == "wisata_custom" else "content"

    for doc_id in doc_ids:
        tv_resp = termvectors_fn(
            index=index_name,
            id=doc_id,
            fields=[field],
            term_statistics=True,
        )
        vector: Dict[str, float] = {}
        term_vectors = tv_resp.get("term_vectors") or {}
        # Prefer the expected field, fall back to the first field present in
        # the response so the helper is resilient to field-name variation.
        info = term_vectors.get(field)
        if info is None and term_vectors:
            info = next(iter(term_vectors.values()))
        terms = (info or {}).get("terms") or {}
        for term_text, stats in terms.items():
            vector[term_text] = float(stats.get("term_freq", 0) or 0)
        results.append({"doc_id": doc_id, "vector": vector})

    return results


def build_rocchio_elasticsearch_query(
    base_query: str,
    weights: Dict[str, float],
    top_k: int = 10,
    index_name: str = "wisata_custom",
) -> dict:
    """Build a boosted Elasticsearch bool query from Rocchio weights.

    Filters terms with positive weight, sorts them by weight descending, and
    maps each to a `match` clause whose `boost` equals the term weight. The
    base query is included as a `must` clause so the original intent is
    preserved, while expansion terms act as `should` clauses.

    Returns a dict with `index` and `body` keys suitable for
    `es_client.search(index=..., body=...)`.
    """
    positive_terms = [
        (term, weight) for term, weight in weights.items() if weight > 0
    ]
    positive_terms.sort(key=lambda item: item[1], reverse=True)
    top_terms = positive_terms[:top_k]

    should_clauses = []
    for term, weight in top_terms:
        should_clauses.append(
            {
                "match": {
                    "content_preprocessed": {
                        "query": term,
                        "boost": weight,
                    }
                }
            }
        )

    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": base_query,
                            "fields": ["title", "content_preprocessed"],
                        }
                    }
                ],
                "should": should_clauses,
                "minimum_should_match": 1 if should_clauses else 0,
            }
        },
        "size": top_k,
    }

    return {"index": index_name, "body": body}


def compute_rocchio_query(
    es_client: Elasticsearch,
    query: str,
    rel_ids: List[str],
    non_rel_ids: List[str],
    alpha: float = 1.0,
    beta: float = 0.75,
    gamma: float = 0.15,
    index_name: str = "wisata_custom",
    top_k: int = 10,
) -> dict:
    """Run the full Rocchio relevance feedback pipeline.

    1. Fetches term vectors for relevant and non-relevant documents.
    2. Calculates Rocchio weights from the query and feedback vectors.
    3. Builds a boosted Elasticsearch query from the weights.

    Returns a dict with `original_query`, `weights`, and
    `elasticsearch_query` keys.
    """
    rel_vecs_response = fetch_term_vectors(es_client, index_name, rel_ids)
    non_rel_vecs_response = fetch_term_vectors(es_client, index_name, non_rel_ids)

    rel_vecs = [entry["vector"] for entry in rel_vecs_response]
    non_rel_vecs = [entry["vector"] for entry in non_rel_vecs_response]

    # Build a simple query vector from the raw query terms (unit weight each).
    query_terms = query.lower().split()
    query_vec = {term: 1.0 for term in query_terms}

    weights = calculate_rocchio_weights(
        query_vec=query_vec,
        rel_vecs=rel_vecs,
        non_rel_vecs=non_rel_vecs,
        alpha=alpha,
        beta=beta,
        gamma=gamma,
    )

    es_query = build_rocchio_elasticsearch_query(
        base_query=query,
        weights=weights,
        top_k=top_k,
        index_name=index_name,
    )

    return {
        "original_query": query,
        "weights": weights,
        "elasticsearch_query": es_query,
    }
