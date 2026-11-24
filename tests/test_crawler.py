"""Unit tests for crawler spiders and raw corpus generation."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

import pytest

from crawler.spiders.base_spider import BaseSpider
from crawler.spiders.indonesiatravel import IndonesiaTravelSpider
from crawler.spiders.nativeindonesia import NativeIndonesiaSpider
from crawler.spiders.wisato import WisatoSpider

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_JSON = REPO_ROOT / "data" / "raw" / "corpus_raw.json"
RAW_CSV = REPO_ROOT / "data" / "raw" / "corpus_raw.csv"


def test_raw_corpus_files_exist():
    assert RAW_JSON.exists(), f"Raw corpus JSON missing at {RAW_JSON}"
    assert RAW_CSV.exists(), f"Raw corpus CSV missing at {RAW_CSV}"


def test_raw_corpus_volume_and_schema():
    with open(RAW_JSON, "r", encoding="utf-8") as f:
        docs = json.load(f)

    assert len(docs) >= 600, f"Expected >= 600 raw documents, found {len(docs)}"
    required_keys = {"doc_id", "title", "content", "url", "source", "location", "category"}

    for doc in docs[:50]:
        assert required_keys.issubset(doc.keys()), f"Missing keys in document: {doc.get('doc_id')}"
        assert len(doc["title"].strip()) > 5, f"Title too short in {doc.get('doc_id')}"
        assert len(doc["content"].strip()) > 100, f"Content too short in {doc.get('doc_id')}"
        assert doc["source"] in {"nativeindonesia", "indonesiatravel", "wisato"}


def test_raw_corpus_csv_matches_json():
    with open(RAW_JSON, "r", encoding="utf-8") as f:
        json_docs = json.load(f)

    with open(RAW_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        csv_docs = list(reader)

    assert len(json_docs) == len(csv_docs), "Row count mismatch between JSON and CSV"
    assert json_docs[0]["doc_id"] == csv_docs[0]["doc_id"]
    assert json_docs[0]["title"] == csv_docs[0]["title"]


def test_spiders_instantiation():
    spiders = [
        NativeIndonesiaSpider(),
        IndonesiaTravelSpider(),
        WisatoSpider(),
    ]
    expected_sources = {"nativeindonesia", "indonesiatravel", "wisato"}
    actual_sources = {spider.source_name for spider in spiders}
    assert actual_sources == expected_sources


def test_spider_clean_text_and_html():
    raw_html = "<div class='content'><p>Pesona pantai kuta di pulau <strong>Bali</strong>.</p></div>"
    cleaned = BaseSpider.strip_html(raw_html)
    assert "<p>" not in cleaned
    assert "<strong>" not in cleaned
    assert "Pesona pantai kuta di pulau Bali." in cleaned


def test_spider_crawl_interface():
    spider = NativeIndonesiaSpider()
    docs = spider.crawl(limit=5)
    assert len(docs) == 5
    for doc in docs:
        assert doc["source"] == "nativeindonesia"
        assert len(doc["title"]) > 5
        assert len(doc["content"]) > 100
