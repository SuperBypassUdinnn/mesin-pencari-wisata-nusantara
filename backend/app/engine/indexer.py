"""Dual-index Elasticsearch setup and posting list inspector for the wisata search engine.

Consumes clean documents (see data/processed/corpus_clean.json) and produces two
Elasticsearch indexes:

- wisata_custom: custom preprocessing fields using the whitespace analyzer, term
  vectors enabled, and two custom similarities (custom_bm25 and custom_lm_dirichlet).
- wisata_baseline: default standard analyzer with default BM25.

Provides index creation, bulk document indexing, and posting list introspection
(df, tf, document pointers) via the _termvectors API.
"""

from __future__ import annotations

from typing import Dict, List

from elasticsearch import helpers

from backend.app.engine.preprocessor import preprocess_text

# ---------------------------------------------------------------------------
# Index names
# ---------------------------------------------------------------------------

INDEX_CUSTOM = "wisata_custom"
INDEX_BASELINE = "wisata_baseline"

ALL_INDEXES = [INDEX_CUSTOM, INDEX_BASELINE]


def _resolve_termvectors_client(es_client):
    """Resolve the termvectors method across elasticsearch client versions.

    elasticsearch 8.x exposes both `termvectors` and `term_vectors`, while older
    7.x clients expose `termvectors`. Return whichever attribute exists so the
    posting list inspector remains resilient across client variations.
    """
    return getattr(es_client, "termvectors", None) or getattr(es_client, "term_vectors", None)

# ---------------------------------------------------------------------------
# Schema mappings
# ---------------------------------------------------------------------------


def get_index_mappings() -> Dict[str, dict]:
    """Return the index mapping bodies for wisata_custom and wisata_baseline.

    Returns a dict keyed by index name. Each value is a body suitable for
    Elasticsearch indices.create with settings (analyzer, similarity) and
    mappings (properties).
    """
    custom_mappings = {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "similarity": {
                    "custom_bm25": {
                        "type": "BM25",
                        "k1": 1.2,
                        "b": 0.75,
                    },
                    "custom_lm_dirichlet": {
                        "type": "LMDirichlet",
                        "mu": 2000,
                    },
                },
                "analysis": {
                    "analyzer": {
                        "whitespace": {
                            "type": "whitespace",
                        }
                    }
                },
            }
        },
        "mappings": {
            "properties": {
                "doc_id": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "whitespace"},
                "content_preprocessed": {
                    "type": "text",
                    "analyzer": "whitespace",
                    "term_vector": "with_positions_offsets_payloads",
                    "similarity": "custom_bm25",
                },
                "url": {"type": "keyword"},
                "source": {"type": "keyword"},
                "location": {"type": "keyword"},
                "category": {"type": "keyword"},
            }
        },
    }

    baseline_mappings = {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "similarity": {
                    "default": {"type": "BM25"},
                },
                "analysis": {
                    "analyzer": {
                        "default": {"type": "standard"},
                    }
                },
            }
        },
        "mappings": {
            "properties": {
                "doc_id": {"type": "keyword"},
                "title": {"type": "text"},
                "content": {
                    "type": "text",
                    "term_vector": "with_positions_offsets_payloads",
                },
                "url": {"type": "keyword"},
                "source": {"type": "keyword"},
                "location": {"type": "keyword"},
                "category": {"type": "keyword"},
            }
        },
    }

    return {
        INDEX_CUSTOM: custom_mappings,
        INDEX_BASELINE: baseline_mappings,
    }


# ---------------------------------------------------------------------------
# Bulk action building
# ---------------------------------------------------------------------------


def _content_field(index_name: str) -> str:
    """Return the content field name for a given index."""
    if index_name == INDEX_CUSTOM:
        return "content_preprocessed"
    return "content"


def build_bulk_actions(docs: List[dict]) -> List[dict]:
    """Build Elasticsearch bulk actions for a list of clean documents.

    Produces two actions per document: one targeting wisata_custom (with
    content_preprocessed) and one targeting wisata_baseline (with raw content).

    Each action dict has _index, _id, and _source keys.
    """
    actions: List[dict] = []
    for doc in docs:
        doc_id = doc.get("doc_id")
        content = doc.get("content", "")
        content_preprocessed = preprocess_text(content)

        custom_source = dict(doc)
        custom_source["content_preprocessed"] = content_preprocessed
        actions.append(
            {
                "_index": INDEX_CUSTOM,
                "_id": doc_id,
                "_source": custom_source,
            }
        )

        baseline_source = dict(doc)
        actions.append(
            {
                "_index": INDEX_BASELINE,
                "_id": doc_id,
                "_source": baseline_source,
            }
        )
    return actions


def index_documents(es_client, docs: List[dict]) -> tuple:
    """Index a list of clean documents into both indexes via the bulk API.

    Returns the (success_count, errors) tuple from elasticsearch.helpers.bulk.
    """
    actions = build_bulk_actions(docs)
    return helpers.bulk(es_client, actions)


# ---------------------------------------------------------------------------
# Index lifecycle
# ---------------------------------------------------------------------------


def create_indexes(es_client) -> List[str]:
    """Idempotently create wisata_custom and wisata_baseline if they do not exist.

    Returns the list of index names that exist after the call.
    """
    mappings = get_index_mappings()
    for index_name, body in mappings.items():
        if not es_client.indices.exists(index=index_name):
            es_client.indices.create(index=index_name, body=body)
    return list(mappings.keys())


# ---------------------------------------------------------------------------
# Posting list inspection
# ---------------------------------------------------------------------------


def extract_posting_list_from_termvectors(termvectors_response: dict) -> dict:
    """Extract per-term statistics from a single-document _termvectors response.

    Returns a dict with a "details" list, where each entry describes one term
    with its field, doc_freq, term_freq, ttf, positions, offsets, and payloads.
    """
    term_vectors = termvectors_response.get("term_vectors") or {}
    details: List[dict] = []
    for field, info in term_vectors.items():
        terms = info.get("terms") or {}
        for term_text, stats in terms.items():
            details.append(
                {
                    "field": field,
                    "term": term_text,
                    "doc_freq": stats.get("doc_freq"),
                    "term_freq": stats.get("term_freq"),
                    "ttf": stats.get("ttf"),
                    "positions": stats.get("positions", []),
                    "offsets": stats.get("offsets", []),
                    "payloads": stats.get("payloads", []),
                }
            )
    return {"details": details}


def get_posting_list(es_client, index_name: str, term: str) -> dict:
    """Retrieve the posting list for a term in an index.

    Searches the index for documents containing the term, then inspects the
    _termvectors of each matching document to gather term frequency. Returns a
    dict with index, field, term, df (document frequency), tf (total term
    frequency across matching docs), and postings (list of {doc_id, term_freq}).
    """
    field = _content_field(index_name)

    search_resp = es_client.search(
        index=index_name,
        body={
            "query": {"match": {field: term}},
            "size": 1000,
            "_source": False,
        },
    )
    hits = search_resp.get("hits", {}).get("hits", [])
    doc_ids = [hit["_id"] for hit in hits]

    termvectors_fn = _resolve_termvectors_client(es_client)
    if termvectors_fn is None:
        raise AttributeError(
            "elasticsearch client exposes neither 'termvectors' nor 'term_vectors'"
        )
    df = len(doc_ids)
    total_tf = 0
    postings: List[dict] = []
    for doc_id in doc_ids:
        tv_resp = termvectors_fn(
            index=index_name,
            id=doc_id,
            fields=[field],
            term_statistics=True,
        )
        stats = extract_posting_list_from_termvectors(tv_resp)
        tf = 0
        for detail in stats.get("details", []):
            if detail.get("term") == term:
                tf = detail.get("term_freq", 0) or 0
                break
        total_tf += tf
        postings.append({"doc_id": doc_id, "term_freq": tf})

    return {
        "index": index_name,
        "field": field,
        "term": term,
        "df": df,
        "tf": total_tf,
        "postings": postings,
    }
