"""Seed script to index local corpus into Elasticsearch."""

import json
import os
import sys
from elasticsearch import Elasticsearch
from backend.app.engine.indexer import create_indexes, index_documents

DEFAULT_ES_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
CORPUS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "data",
    "processed",
    "corpus_clean.json"
)

def run_seed(es_url: str = DEFAULT_ES_URL, corpus_file: str = CORPUS_PATH) -> int:
    """Load corpus from JSON file and index into Elasticsearch."""
    if not os.path.exists(corpus_file):
        print(f"Error: Corpus file not found at {corpus_file}")
        return 1

    with open(corpus_file, "r", encoding="utf-8") as f:
        docs = json.load(f)

    print(f"Loaded {len(docs)} documents from {corpus_file}")
    es = Elasticsearch(es_url)
    if not es.ping():
        print(f"Error: Unable to connect to Elasticsearch at {es_url}")
        return 1

    print("Connected to Elasticsearch. Creating indexes if not present...")
    create_indexes(es)

    print("Indexing documents into wisata_custom and wisata_baseline...")
    success, failed = index_documents(es, docs)
    print(f"Indexing completed: {success} successful actions, {failed} failed.")
    return 0

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ES_URL
    sys.exit(run_seed(url))
