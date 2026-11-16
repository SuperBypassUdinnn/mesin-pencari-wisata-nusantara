"""FastAPI REST API endpoint tests for the wisata search engine backend.

These tests exercise the API layer with mocked Elasticsearch and mocked engine
functions so they run deterministically without a live search cluster.
"""

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "mesin-pencari-wisata-nusantara"
    assert data["group"] == "Kelompok 10"


@patch("backend.app.api.routes.get_es_client")
def test_search_endpoint(mock_get_es):
    mock_es = MagicMock()
    mock_get_es.return_value = mock_es
    with patch("backend.app.api.routes.search_documents") as mock_search:
        mock_search.return_value = {
            "query": "pantai bali",
            "model": "bm25",
            "latency_ms": 15.2,
            "total_hits": 1,
            "results": [
                {"rank": 1, "score": 10.5, "title": "Pantai Kuta", "url": "https://example.com"}
            ],
        }
        response = client.get("/api/search?q=pantai+bali&model=bm25")
        assert response.status_code == 200
        data = response.json()
        assert data["total_hits"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["title"] == "Pantai Kuta"


@patch("backend.app.api.routes.get_es_client")
@patch("backend.app.api.routes.expand_query")
@patch("backend.app.api.routes.search_documents")
def test_search_endpoint_with_expansion(mock_search, mock_expand, mock_get_es):
    mock_get_es.return_value = MagicMock()
    mock_expand.return_value = {
        "original": "pantai bali",
        "expanded": "pantai bali bahari laut",
        "has_expansion": True,
        "added_synonyms": ["bahari", "laut"],
    }
    mock_search.return_value = {
        "query": "pantai bali bahari laut",
        "model": "bm25",
        "latency_ms": 12.0,
        "total_hits": 2,
        "results": [],
    }
    response = client.get("/api/search?q=pantai+bali&model=bm25&expand=true")
    assert response.status_code == 200
    data = response.json()
    assert data["total_hits"] == 2
    mock_expand.assert_called_once_with("pantai bali")
    # The expanded query text should be forwarded to the search engine.
    assert mock_search.call_args.args[1] == "pantai bali bahari laut"


@patch("backend.app.api.routes.get_es_client")
@patch("backend.app.api.routes.search_documents")
def test_search_endpoint_dual_model(mock_search, mock_get_es):
    mock_get_es.return_value = MagicMock()
    mock_search.side_effect = [
        {
            "query": "pantai bali",
            "model": "bm25",
            "latency_ms": 10.0,
            "total_hits": 2,
            "results": [{"rank": 1, "score": 9.0, "title": "Pantai A"}],
        },
        {
            "query": "pantai bali",
            "model": "lm_dirichlet",
            "latency_ms": 11.0,
            "total_hits": 1,
            "results": [{"rank": 1, "score": 8.0, "title": "Pantai B"}],
        },
    ]
    response = client.get("/api/search?q=pantai+bali&model=both")
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "both"
    assert "bm25" in data["results"]
    assert "lm_dirichlet" in data["results"]
    assert data["results"]["bm25"]["total_hits"] == 2
    assert data["results"]["lm_dirichlet"]["total_hits"] == 1
    assert mock_search.call_count == 2


@patch("backend.app.api.routes.get_es_client")
@patch("backend.app.api.routes.compute_rocchio_query")
def test_rocchio_feedback_endpoint(mock_compute_rocchio, mock_get_es):
    mock_get_es.return_value = MagicMock()
    mock_get_es.return_value.search.return_value = {
        "hits": {"hits": []}
    }
    mock_compute_rocchio.return_value = {
        "original_query": "pantai bali",
        "weights": {"pantai": 1.0, "bali": 0.8},
        "elasticsearch_query": {
            "index": "wisata_custom",
            "body": {"query": {"bool": {}}, "size": 10},
        },
    }
    response = client.post(
        "/api/feedback/rocchio",
        json={
            "query": "pantai bali",
            "relevant_doc_ids": ["doc_1"],
            "non_relevant_doc_ids": [],
            "alpha": 1.0,
            "beta": 0.75,
            "gamma": 0.15,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["original_query"] == "pantai bali"
    assert data["weights"] == {"pantai": 1.0, "bali": 0.8}
    mock_compute_rocchio.assert_called_once()


@patch("backend.app.api.routes.inspect_preprocessing")
def test_inspect_preprocessing_endpoint(mock_inspect):
    mock_inspect.return_value = {
        "raw": "Pantai Kuta",
        "case_folded": "pantai kuta",
        "cleaned": "pantai kuta",
        "tokens": ["pantai", "kuta"],
        "filtered": ["pantai", "kuta"],
        "stemmed": ["pantai", "kuta"],
    }
    response = client.get("/api/inspect/preprocessing?text=Pantai+Kuta")
    assert response.status_code == 200
    data = response.json()
    assert data["tokens"] == ["pantai", "kuta"]
    assert data["stemmed"] == ["pantai", "kuta"]
    mock_inspect.assert_called_once_with("Pantai Kuta")


@patch("backend.app.api.routes.inspect_preprocessing")
def test_inspect_preprocessing_endpoint_uses_q_param(mock_inspect):
    mock_inspect.return_value = {
        "raw": "curug cipendok",
        "case_folded": "curug cipendok",
        "cleaned": "curug cipendok",
        "tokens": ["curug", "cipendok"],
        "filtered": ["curug", "cipendok"],
        "stemmed": ["curug", "cipendok"],
    }
    response = client.get("/api/inspect/preprocessing?q=curug+cipendok")
    assert response.status_code == 200
    mock_inspect.assert_called_once_with("curug cipendok")


@patch("backend.app.api.routes.get_es_client")
@patch("backend.app.api.routes.get_posting_list")
def test_inspect_posting_list_endpoint(mock_get_posting_list, mock_get_es):
    mock_get_es.return_value = MagicMock()
    mock_get_posting_list.return_value = {
        "index": "wisata_custom",
        "field": "content_preprocessed",
        "term": "pantai",
        "df": 3,
        "tf": 5,
        "postings": [{"doc_id": "doc_1", "term_freq": 2}],
    }
    response = client.get("/api/inspect/posting-list?term=pantai&index=wisata_custom")
    assert response.status_code == 200
    data = response.json()
    assert data["term"] == "pantai"
    assert data["df"] == 3
    assert data["tf"] == 5
    assert data["index"] == "wisata_custom"


def test_evaluation_endpoint():
    response = client.get("/api/evaluation")
    assert response.status_code == 200
    data = response.json()
    assert "available" in data
    assert "benchmarks" in data
