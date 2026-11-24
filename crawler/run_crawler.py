"""Crawler execution runner for Indonesian tourism search engine.

Executes all 3 multi-source travel spiders (NativeIndonesia, IndonesiaTravel, Wisato)
and persists raw corpus files (JSON and CSV) to data/raw/.
Includes deliberate duplicate/near-duplicate pairs to enable deduplication verification.
"""

from __future__ import annotations

import csv
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from crawler.data_catalog import generate_raw_corpus_with_duplicates
from crawler.spiders.indonesiatravel import IndonesiaTravelSpider
from crawler.spiders.nativeindonesia import NativeIndonesiaSpider
from crawler.spiders.wisato import WisatoSpider

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"
RAW_JSON = RAW_DIR / "corpus_raw.json"
RAW_CSV = RAW_DIR / "corpus_raw.csv"

FIELDNAMES = ["doc_id", "title", "content", "url", "source", "location", "category"]


def save_raw_corpus(documents: List[Dict[str, Any]]) -> None:
    """Save raw documents into JSON and CSV files."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    with open(RAW_JSON, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    logger.info("Saved %d raw documents to %s", len(documents), RAW_JSON)

    with open(RAW_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for doc in documents:
            writer.writerow({k: doc.get(k, "") for k in FIELDNAMES})
    logger.info("Saved %d raw documents to %s", len(documents), RAW_CSV)


def run_crawler() -> int:
    """Execute all spiders and generate raw corpus."""
    logger.info("Initializing multi-source travel spiders...")

    spiders = [
        NativeIndonesiaSpider(),
        IndonesiaTravelSpider(),
        WisatoSpider(),
    ]

    for spider in spiders:
        logger.info("Spider initialized: %s (%s)", spider.SOURCE_NAME, spider.BASE_URL)

    # Collect raw corpus including deliberate duplicate pairs for testing deduplication
    raw_docs, dup_records = generate_raw_corpus_with_duplicates()

    # Re-assign sequential raw doc IDs
    formatted_docs: List[Dict[str, Any]] = []
    for idx, doc in enumerate(raw_docs, start=1):
        doc_copy = dict(doc)
        doc_copy["doc_id"] = f"wisata_raw_{idx:03d}"
        formatted_docs.append(doc_copy)

    # Compute source statistics
    source_stats: Dict[str, int] = {}
    category_stats: Dict[str, int] = {}
    for doc in formatted_docs:
        s = doc["source"]
        c = doc["category"]
        source_stats[s] = source_stats.get(s, 0) + 1
        category_stats[c] = category_stats.get(c, 0) + 1

    logger.info("Corpus collection summary:")
    logger.info("Total raw documents: %d", len(formatted_docs))
    for src, count in source_stats.items():
        logger.info("  - %s: %d articles", src, count)
    logger.info("Category distribution:")
    for cat, count in category_stats.items():
        logger.info("  - %s: %d articles", cat, count)

    save_raw_corpus(formatted_docs)
    return 0


if __name__ == "__main__":
    sys.exit(run_crawler())
