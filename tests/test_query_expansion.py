from backend.app.engine.query_expansion import expand_query, get_synonym_dictionary


def test_synonym_dictionary_count():
    synonyms = get_synonym_dictionary()
    assert len(synonyms) >= 15, f"Expected >= 15 synonym pairs, found {len(synonyms)}"
    assert "curug" in synonyms and "air terjun" in synonyms["curug"]


def test_expand_query_transformation():
    original = "curug bogor"
    expanded = expand_query(original)
    assert expanded["original"] == original
    assert "air terjun" in expanded["expanded"]
    assert expanded["has_expansion"] is True


def test_expand_query_no_expansion_when_no_match():
    original = "xyzzy unknown term"
    expanded = expand_query(original)
    assert expanded["original"] == original
    assert expanded["has_expansion"] is False


def test_expand_query_returns_expected_keys():
    expanded = expand_query("pantai bali")
    assert set(expanded.keys()) == {"original", "expanded", "has_expansion", "added_synonyms"}
    assert isinstance(expanded["added_synonyms"], list)


def test_synonym_dictionary_is_bidirectional():
    synonyms = get_synonym_dictionary()
    for term, syn_list in synonyms.items():
        for syn in syn_list:
            assert term in synonyms.get(syn, []), f"{term} not in synonyms[{syn}]"
