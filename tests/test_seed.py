"""Unit tests for seed script."""

import json
from unittest.mock import MagicMock, patch
from backend.app.engine.seed import run_seed

def test_run_seed_with_mock_es(tmp_path):
    sample_docs = [
        {
            "doc_id": "wisata_seed_001",
            "title": "Pantai Kuta",
            "content": "Pasir putih di Bali...",
            "url": "https://example.com/kuta",
            "source": "nativeindonesia",
            "location": "Bali",
            "category": "Wisata Bahari"
        }
    ]
    corpus_file = tmp_path / "corpus_clean.json"
    corpus_file.write_text(json.dumps(sample_docs), encoding="utf-8")

    with patch("backend.app.engine.seed.Elasticsearch") as mock_es_cls:
        mock_es = MagicMock()
        mock_es.ping.return_value = True
        mock_es_cls.return_value = mock_es

        with patch("backend.app.engine.seed.create_indexes") as mock_create, \
             patch("backend.app.engine.seed.index_documents") as mock_index:
            mock_index.return_value = (2, [])
            exit_code = run_seed(es_url="http://mock:9200", corpus_file=str(corpus_file))
            assert exit_code == 0
            mock_create.assert_called_once_with(mock_es)
            mock_index.assert_called_once_with(mock_es, sample_docs)
