from unittest.mock import MagicMock, patch
from backend.app.engine.indexer import (
    get_index_mappings,
    build_bulk_actions,
    extract_posting_list_from_termvectors,
    create_indexes,
    index_documents,
    get_posting_list,
)

def test_index_mappings_configuration():
    mappings = get_index_mappings()
    assert "wisata_custom" in mappings and "wisata_baseline" in mappings
    # Check custom index analyzer and similarities
    custom_settings = mappings["wisata_custom"]["settings"]
    assert "similarity" in custom_settings["index"]
    assert "custom_bm25" in custom_settings["index"]["similarity"]
    assert "custom_lm_dirichlet" in custom_settings["index"]["similarity"]
    # Check term_vector enabled
    custom_props = mappings["wisata_custom"]["mappings"]["properties"]
    assert custom_props["content_preprocessed"]["term_vector"] == "with_positions_offsets_payloads"

def test_build_bulk_actions():
    sample_doc = {
        "doc_id": "wisata_001",
        "title": "Curug Leuwi Hejo",
        "content": "Air terjun alami di Bogor...",
        "url": "https://example.com",
        "source": "nativeindonesia",
        "location": "Bogor",
        "category": "Wisata Alam"
    }
    actions = build_bulk_actions([sample_doc])
    assert len(actions) == 2  # One for wisata_custom, one for wisata_baseline
    assert actions[0]["_index"] == "wisata_custom"
    assert "content_preprocessed" in actions[0]["_source"]
    assert actions[1]["_index"] == "wisata_baseline"
    assert "content" in actions[1]["_source"]


def test_extract_posting_list_from_termvectors():
    response = {
        "term_vectors": {
            "content_preprocessed": {
                "terms": {
                    "curug": {
                        "doc_freq": 3,
                        "term_freq": 1,
                        "ttf": 5,
                        "positions": [2],
                        "offsets": [{"start": 0, "end": 5}],
                        "payloads": [],
                    },
                    "air": {
                        "doc_freq": 2,
                        "term_freq": 1,
                        "ttf": 4,
                        "positions": [0],
                        "offsets": [{"start": 0, "end": 3}],
                        "payloads": [],
                    },
                }
            }
        }
    }
    result = extract_posting_list_from_termvectors(response)
    assert "details" in result
    details = result["details"]
    assert len(details) == 2
    curug = next(d for d in details if d["term"] == "curug")
    assert curug["field"] == "content_preprocessed"
    assert curug["doc_freq"] == 3
    assert curug["term_freq"] == 1
    assert curug["ttf"] == 5
    assert curug["positions"] == [2]


def test_create_indexes_creates_missing_indexes():
    es_client = MagicMock()
    es_client.indices.exists.return_value = False
    es_client.indices.create.return_value = {"acknowledged": True}

    created = create_indexes(es_client)

    assert "wisata_custom" in created and "wisata_baseline" in created
    assert es_client.indices.create.call_count == 2
    es_client.indices.create.assert_any_call(
        index="wisata_custom",
        body=get_index_mappings()["wisata_custom"],
    )
    es_client.indices.create.assert_any_call(
        index="wisata_baseline",
        body=get_index_mappings()["wisata_baseline"],
    )


def test_create_indexes_skips_existing_indexes():
    es_client = MagicMock()
    es_client.indices.exists.return_value = True

    created = create_indexes(es_client)

    assert "wisata_custom" in created and "wisata_baseline" in created
    es_client.indices.create.assert_not_called()


def test_index_documents_calls_bulk():
    sample_doc = {
        "doc_id": "wisata_001",
        "title": "Curug Leuwi Hejo",
        "content": "Air terjun alami di Bogor...",
        "url": "https://example.com",
        "source": "nativeindonesia",
        "location": "Bogor",
        "category": "Wisata Alam",
    }
    es_client = MagicMock()
    with patch("backend.app.engine.indexer.helpers.bulk", return_value=(2, [])) as mock_bulk:
        success, errors = index_documents(es_client, [sample_doc])
        assert success == 2
        assert errors == []
        mock_bulk.assert_called_once()
        args, _ = mock_bulk.call_args
        assert args[0] is es_client
        actions = args[1]
        assert len(actions) == 2
        assert actions[0]["_index"] == "wisata_custom"
        assert actions[1]["_index"] == "wisata_baseline"


def test_get_posting_list_with_mock_client():
    es_client = MagicMock()

    search_resp = {
        "hits": {
            "hits": [
                {"_id": "wisata_001"},
                {"_id": "wisata_002"},
            ]
        }
    }
    es_client.search.return_value = search_resp

    def fake_termvectors(index, id, fields, term_statistics):
        return {
            "term_vectors": {
                fields[0]: {
                    "terms": {
                        "curug": {
                            "doc_freq": 2,
                            "term_freq": 1,
                            "ttf": 2,
                            "positions": [0],
                            "offsets": [],
                            "payloads": [],
                        }
                    }
                }
            }
        }

    es_client.termvectors.side_effect = fake_termvectors

    result = get_posting_list(es_client, "wisata_custom", "curug")

    assert result["index"] == "wisata_custom"
    assert result["term"] == "curug"
    assert result["df"] == 2
    assert result["tf"] == 2
    assert len(result["postings"]) == 2
    assert result["postings"][0] == {"doc_id": "wisata_001", "term_freq": 1}
    assert result["postings"][1] == {"doc_id": "wisata_002", "term_freq": 1}
    es_client.search.assert_called_once()
