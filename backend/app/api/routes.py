"""REST API routes for the wisata search engine backend.

Wires the core IR engine modules (preprocessor, indexer, searcher,
query_expansion, rocchio) into HTTP endpoints under the /api prefix.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

from backend.app.engine.preprocessor import inspect_preprocessing
from backend.app.engine.query_expansion import expand_query
from backend.app.engine.rocchio import compute_rocchio_query
from backend.app.engine.searcher import (
    INDEX_CUSTOM,
    _extract_hits,
    format_search_hit,
    search_documents,
)
from backend.app.engine.indexer import get_posting_list

from backend.app.api.schemas import (
    InspectPreprocessingResponse,
    PostingListResponse,
    RocchioFeedbackRequest,
    RocchioFeedbackResponse,
)

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter()

# Evaluation benchmark file produced by the automated evaluator (Member 4).
EVALUATION_RESULTS_PATH = Path("data/ground_truth/evaluation_results.json")

DEFAULT_MODEL = "bm25"
DEFAULT_TOP_K = 10
DUAL_MODELS = {"both", "split"}


# ---------------------------------------------------------------------------
# Elasticsearch client helper
# ---------------------------------------------------------------------------

def get_es_client():
    """Create an Elasticsearch client pointed at the local development node.

    In unit tests this function is patched (see tests/test_api.py) so no live
    Elasticsearch cluster is required.
    """
    from elasticsearch import Elasticsearch

    return Elasticsearch(
        hosts=["http://localhost:9200"],
        verify_certs=False,
        ssl_show_warn=False,
        request_timeout=10,
    )


# ---------------------------------------------------------------------------
# Response normalization helpers
# ---------------------------------------------------------------------------

def _normalize_search_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a search_documents result into a stable response dict.

    The engine emits total_hits as `total`; the API exposes both `total` and
    `total_hits` so callers can rely on either key.
    """
    total = result.get("total", result.get("total_hits", 0))
    return {
        "query": result.get("query"),
        "model": result.get("model"),
        "index": result.get("index"),
        "top_k": result.get("top_k"),
        "latency_ms": result.get("latency_ms"),
        "total": total,
        "total_hits": total,
        "results": result.get("results", []),
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/health")
def health() -> Dict[str, str]:
    """Liveness endpoint confirming the API is up."""
    return {
        "status": "ok",
        "app": "mesin-pencari-wisata-nusantara",
        "group": "Kelompok 10",
    }


@router.get("/search")
def search(
    q: str = Query(..., description="Search query text"),
    model: str = Query(DEFAULT_MODEL, description="Retrieval model: bm25, lm_dirichlet, baseline, or both/split"),
    expand: bool = Query(False, description="Apply synonym query expansion before searching"),
    top_k: int = Query(DEFAULT_TOP_K, ge=1, le=1000, description="Maximum number of results"),
) -> Dict[str, Any]:
    """Execute a ranked search, optionally with synonym expansion and dual-model output."""
    es_client = get_es_client()

    query_text = q
    expansion_info = None
    if expand:
        expansion_info = expand_query(q)
        query_text = expansion_info.get("expanded", q)

    normalized_model = model.lower()
    if normalized_model in DUAL_MODELS:
        bm25_result = search_documents(es_client, query_text, "bm25", top_k=top_k)
        lm_result = search_documents(es_client, query_text, "lm_dirichlet", top_k=top_k)
        return {
            "query": q,
            "model": "both",
            "expand": expand,
            "top_k": top_k,
            "expansion": expansion_info,
            "results": {
                "bm25": _normalize_search_result(bm25_result),
                "lm_dirichlet": _normalize_search_result(lm_result),
            },
        }

    try:
        result = search_documents(es_client, query_text, normalized_model, top_k=top_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    normalized = _normalize_search_result(result)
    return {
        "query": q,
        "model": normalized_model,
        "expand": expand,
        "top_k": top_k,
        "expansion": expansion_info,
        **normalized,
    }


@router.post("/feedback/rocchio", response_model=RocchioFeedbackResponse)
def rocchio_feedback(payload: RocchioFeedbackRequest) -> Dict[str, Any]:
    """Run Rocchio relevance feedback and return re-ranked search results."""
    es_client = get_es_client()

    rocchio_result = compute_rocchio_query(
        es_client=es_client,
        query=payload.query,
        rel_ids=payload.relevant_doc_ids,
        non_rel_ids=payload.non_relevant_doc_ids,
        alpha=payload.alpha,
        beta=payload.beta,
        gamma=payload.gamma,
        index_name=INDEX_CUSTOM,
    )

    es_query = rocchio_result.get("elasticsearch_query", {})
    search_response = es_client.search(index=es_query.get("index", INDEX_CUSTOM), body=es_query.get("body", {}))
    hits = _extract_hits(search_response) if isinstance(search_response, dict) else []
    results = [format_search_hit(hit, rank=position + 1) for position, hit in enumerate(hits)]

    return {
        "original_query": rocchio_result.get("original_query", payload.query),
        "weights": rocchio_result.get("weights", {}),
        "results": results,
    }


@router.get("/inspect/preprocessing", response_model=InspectPreprocessingResponse)
def inspect_preprocessing_route(
    q: Optional[str] = Query(None, description="Text to inspect"),
    text: Optional[str] = Query(None, description="Alternative text parameter"),
) -> Dict[str, Any]:
    """Return step-by-step preprocessing streams for a single input text."""
    input_text = q if q is not None else text
    if input_text is None:
        raise HTTPException(status_code=400, detail="Provide a 'q' or 'text' query parameter")
    return inspect_preprocessing(input_text)


@router.get("/inspect/posting-list", response_model=PostingListResponse)
def inspect_posting_list(
    term: str = Query(..., description="Term to inspect"),
    index: str = Query("wisata_custom", description="Target index name"),
) -> Dict[str, Any]:
    """Return posting list statistics (df, tf, document pointers) for a term."""
    es_client = get_es_client()
    return get_posting_list(es_client, index, term)


@router.get("/evaluation")
def evaluation() -> Dict[str, Any]:
    """Return evaluation benchmarks from the ground truth file if available."""
    if EVALUATION_RESULTS_PATH.exists():
        try:
            payload = json.loads(EVALUATION_RESULTS_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise HTTPException(status_code=500, detail=f"Failed to read evaluation results: {exc}")
        if isinstance(payload, dict):
            return {"available": True, "source": str(EVALUATION_RESULTS_PATH), **payload}
        return {"available": True, "source": str(EVALUATION_RESULTS_PATH), "benchmarks": payload}

    return {
        "available": False,
        "source": str(EVALUATION_RESULTS_PATH),
        "benchmarks": [],
        "note": "No precomputed evaluation results found; run the evaluator to generate benchmarks.",
    }
