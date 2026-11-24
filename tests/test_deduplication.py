"""Unit tests for deduplication pipeline and clean corpus validation."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

import pytest

from scripts.check_duplicates import compute_similarity, deduplicate_corpus

REPO_ROOT = Path(__file__).resolve().parents[1]
CLEAN_JSON = REPO_ROOT / "data" / "processed" / "corpus_clean.json"
CLEAN_CSV = REPO_ROOT / "data" / "processed" / "corpus_clean.csv"
REPORT_MD = REPO_ROOT / "docs" / "evidence" / "duplicate_report.md"


def test_compute_similarity_exact_and_near():
    text1 = "pantai kuta bali merupakan destinasi wisata populer dengan pasir putih"
    text2 = "pantai kuta bali merupakan destinasi wisata populer dengan pasir putih"
    text3 = "curug leuwi hejo bogor air terjun alami jernih dan sejuk"
    assert compute_similarity(text1, text2) >= 0.99
    assert compute_similarity(text1, text3) < 0.30


def test_clean_corpus_minimum_unique():
    assert CLEAN_JSON.exists(), f"Clean corpus missing at {CLEAN_JSON}"
    with open(CLEAN_JSON, "r", encoding="utf-8") as f:
        clean_docs = json.load(f)
    assert len(clean_docs) >= 500, f"Expected >= 500 unique docs, found {len(clean_docs)}"


def test_clean_corpus_schema():
    with open(CLEAN_JSON, "r", encoding="utf-8") as f:
        clean_docs = json.load(f)

    required_keys = {"doc_id", "title", "content", "url", "source", "location", "category"}
    for doc in clean_docs[:50]:
        assert required_keys.issubset(doc.keys()), f"Missing keys in document: {doc.get('doc_id')}"
        assert len(doc["title"].strip()) > 5
        assert len(doc["content"].strip()) > 100
        assert doc["source"] in {"nativeindonesia", "indonesiatravel", "wisato"}


def test_clean_corpus_csv_matches_json():
    assert CLEAN_CSV.exists(), f"Clean CSV missing at {CLEAN_CSV}"
    with open(CLEAN_JSON, "r", encoding="utf-8") as f:
        json_docs = json.load(f)
    with open(CLEAN_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        csv_docs = list(reader)

    assert len(json_docs) == len(csv_docs)
    assert json_docs[0]["doc_id"] == csv_docs[0]["doc_id"]


def test_deduplication_removes_synthetic_duplicates():
    base_content = (
        "Pantai Parangtritis di pesisir selatan Bantul Yogyakarta menyajikan pemandangan matahari "
        "terbenam yang memikat dihiasi deburan ombak Samudera Hindia yang dahsyat dan gumuk pasir "
        "pantai yang luas membentang indah."
    )
    sample_docs = [
        {
            "doc_id": "test_001",
            "title": "Wisata Pantai Parangtritis Jogja",
            "content": base_content,
            "url": "https://example.com/parangtritis",
            "source": "nativeindonesia",
            "location": "Bantul, D.I. Yogyakarta",
            "category": "Wisata Bahari",
        },
        {
            "doc_id": "test_002",
            "title": "Wisata Pantai Parangtritis Jogja",
            "content": base_content,
            "url": "https://example.com/parangtritis?ref=copy",
            "source": "nativeindonesia",
            "location": "Bantul, D.I. Yogyakarta",
            "category": "Wisata Bahari",
        },
        {
            "doc_id": "test_003",
            "title": "Wisata Pantai Parangtritis Jogja",
            "content": base_content + " Menarik.",
            "url": "https://example.com/parangtritis?source=app",
            "source": "nativeindonesia",
            "location": "Bantul, D.I. Yogyakarta",
            "category": "Wisata Bahari",
        },
        {
            "doc_id": "test_004",
            "title": "Pesona Danau Toba Sumatera Utara",
            "content": (
                "Danau Toba merupakan danau vulkanik terbesar di dunia dengan pemandangan perbukitan "
                "hijau yang memukau dan udara pegunungan yang sangat sejuk menyegarkan wisatawan."
            ),
            "url": "https://example.com/danau-toba",
            "source": "indonesiatravel",
            "location": "Toba, Sumatera Utara",
            "category": "Wisata Alam",
        },
    ]
    clean, removed = deduplicate_corpus(sample_docs, threshold=0.95)
    assert len(clean) == 2
    assert len(removed) == 2
    clean_ids = {d["doc_id"] for d in clean}
    assert "test_001" in clean_ids
    assert "test_004" in clean_ids


def test_duplicate_report_exists_and_verified():
    assert REPORT_MD.exists(), f"Duplicate report missing at {REPORT_MD}"
    content = REPORT_MD.read_text(encoding="utf-8")
    assert "Corpus Deduplication Verification Report" in content
    assert "Final Clean Corpus Count" in content
    assert "Compliance Status: Verified" in content
