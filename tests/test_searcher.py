from backend.app.engine.searcher import build_search_query, format_search_hit

def test_build_search_query_bm25_vs_lm_vs_baseline():
    q_bm25 = build_search_query(query_text="pantai pasir putih", model="bm25", top_k=10)
    assert q_bm25["index"] == "wisata_custom"
    assert "content_preprocessed" in str(q_bm25["body"])
    
    q_lm = build_search_query(query_text="pantai pasir putih", model="lm_dirichlet", top_k=10)
    assert q_lm["index"] == "wisata_custom"
    
    q_baseline = build_search_query(query_text="pantai pasir putih", model="baseline", top_k=10)
    assert q_baseline["index"] == "wisata_baseline"
    assert "content" in str(q_baseline["body"])

def test_format_search_hit():
    mock_hit = {
        "_id": "wisata_001",
        "_score": 12.45,
        "_source": {
            "title": "Pantai Kuta Bali",
            "content": "Pantai pasir putih dengan pemandangan matahari terbenam yang memukau...",
            "url": "https://example.com/pantai-kuta",
            "source": "nativeindonesia",
            "location": "Bali",
            "category": "Wisata Bahari"
        },
        "highlight": {"content": ["Pantai <em>pasir putih</em> dengan pemandangan..."]}
    }
    formatted = format_search_hit(mock_hit, rank=1)
    assert formatted["rank"] == 1
    assert formatted["score"] == 12.45
    assert formatted["title"] == "Pantai Kuta Bali"
    assert "snippet" in formatted
