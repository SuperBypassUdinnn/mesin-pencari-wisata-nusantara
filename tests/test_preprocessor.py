from backend.app.engine.preprocessor import preprocess_text, inspect_preprocessing


def test_preprocess_cleaning_and_stemming():
    raw_text = "<p>Harga tiket masuk Rp 15.000,- per orang! Pemandangan indah di pantai kuta bali. Buka 08.00-17.00 WIB. Baca juga artikel menarik lainnya.</p>"
    processed = preprocess_text(raw_text)

    # HTML and prices must be stripped
    assert "<p>" not in processed and "15.000" not in processed
    # Noise words like 'baca', 'artikel' must be filtered by travel stopwords
    assert "baca" not in processed.split()
    assert "artikel" not in processed.split()
    # Tourism domain keywords like 'pantai' must be preserved
    assert "pantai" in processed.split()
    # 'keindahan' / 'pemandangan' should be stemmed to root 'indah' / 'pandang'
    assert "indah" in processed.split() or "pandang" in processed.split()


def test_inspect_preprocessing():
    sample = "Pesona air terjun curug bogor yang sangat memukau."
    result = inspect_preprocessing(sample)
    assert "raw" in result and "tokens" in result and "stemmed" in result
    assert isinstance(result["tokens"], list)
