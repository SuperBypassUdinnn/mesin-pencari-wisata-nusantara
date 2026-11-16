from unittest.mock import MagicMock
from backend.app.engine.indexer import (
    get_index_mappings,
    build_bulk_actions,
    extract_posting_list_from_termvectors
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
