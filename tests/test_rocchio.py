from unittest.mock import MagicMock

from backend.app.engine.rocchio import (
    calculate_rocchio_weights,
    fetch_term_vectors,
    build_rocchio_elasticsearch_query,
    compute_rocchio_query,
)


def test_calculate_rocchio_weights():
    query_vector = {"pantai": 1.0, "bali": 1.0}
    rel_vectors = [{"pantai": 3.0, "pasir": 2.0, "putih": 2.0}]
    non_rel_vectors = [{"hotel": 4.0, "villa": 2.0}]

    weights = calculate_rocchio_weights(
        query_vec=query_vector,
        rel_vecs=rel_vectors,
        non_rel_vecs=non_rel_vectors,
        alpha=1.0,
        beta=0.75,
        gamma=0.15,
    )
    assert weights["pantai"] > 1.0
    assert weights.get("pasir", 0) > 0
    assert weights.get("hotel", 0) <= 0


def test_fetch_term_vectors_returns_normalized_list():
    es_client = MagicMock()
    es_client.termvectors.return_value = {
        "term_vectors": {
            "content": {
                "terms": {
                    "pantai": {"term_freq": 3},
                    "pasir": {"term_freq": 2},
                }
            }
        }
    }

    result = fetch_term_vectors(es_client, "wisata_custom", ["doc_1"])

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["doc_id"] == "doc_1"
    assert result[0]["vector"] == {"pantai": 3, "pasir": 2}
    es_client.termvectors.assert_called_once()


def test_build_rocchio_elasticsearch_query_structure():
    weights = {"pantai": 2.5, "pasir": 1.5, "hotel": -0.5}
    query_body = build_rocchio_elasticsearch_query(
        base_query="pantai bali", weights=weights, top_k=10, index_name="wisata_custom"
    )
    assert query_body["index"] == "wisata_custom"
    assert "query" in query_body["body"]
    assert "bool" in query_body["body"]["query"]


def test_compute_rocchio_query_with_mock_client():
    es_client = MagicMock()
    es_client.termvectors.return_value = {
        "term_vectors": {
            "content": {
                "terms": {
                    "pantai": {"term_freq": 3},
                    "pasir": {"term_freq": 2},
                }
            }
        }
    }
    es_client.search.return_value = {"hits": {"hits": [], "total": {"value": 0}}}

    result = compute_rocchio_query(
        es_client,
        query="pantai bali",
        rel_ids=["doc_1"],
        non_rel_ids=["doc_2"],
        alpha=1.0,
        beta=0.75,
        gamma=0.15,
        index_name="wisata_custom",
        top_k=10,
    )
    assert "original_query" in result
    assert "weights" in result
    assert "elasticsearch_query" in result
