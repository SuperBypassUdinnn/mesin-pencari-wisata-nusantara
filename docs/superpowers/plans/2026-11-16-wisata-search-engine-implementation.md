# Indonesian Tourism Vertical Search Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and deliver an end-to-end Indonesian Tourism Vertical Search Engine (**Mesin Pencari Wisata Nusantara**) for Kelompok 10, featuring multi-source crawled corpus ($\ge 500$ unique docs), custom Sastrawi preprocessing, dual-index Elasticsearch (Lucene), Okapi BM25 vs. LM Dirichlet retrieval, Query Expansion, interactive Rocchio Relevance Feedback, quantitative IR evaluation (P@10, Recall, F1, MAP), and a React Vite web UI containerized via Docker Compose.

**Architecture:** Three-tier containerized client-server system consisting of an official Elasticsearch 8.13.x container (managing isolated `wisata_custom` and `wisata_baseline` indexes), a Python 3.11 FastAPI backend orchestrating Sastrawi preprocessing, retrieval algorithms, term vectors, and evaluation, and a React 18 + Tailwind CSS frontend delivering real-time search, side-by-side split comparison, and an analytics dashboard.

**Tech Stack:** Python 3.11, FastAPI, PySastrawi, Elasticsearch 8.13 (`elasticsearch-py`), React 18, Vite, Tailwind CSS, Lucide Icons, Recharts, Docker & Docker Compose, Pytest.

**Spec:** `docs/superpowers/specs/2026-11-16-wisata-search-engine-design.md`

## Global Constraints

- Never mention or include artificial timelines, deadlines, or duration estimates (such as "1 minggu", "2 minggu", or "14 hari") in repository documentation, code, trackers, or reports unless explicitly requested by the user.
- Strictly adhere to the Clean Text Policy: zero decorative icons or pictographic emojis in commit messages, documentation, code comments, or PR descriptions.
- Language standardization: Formal technical English for all engineering files (code, tests, docstrings, commit messages, technical docs).
- Minimum corpus volume: Crawl 600 to 800 documents; verify $\ge 500$ unique documents after $>95\%$ text deduplication.
- Dual-index Lucene architecture: Preprocessed tokens indexed with `WhitespaceAnalyzer` in `wisata_custom`; raw text indexed with `StandardAnalyzer` in `wisata_baseline`.
- Two ranked retrieval models from distinct similarity families: Okapi BM25 ($k_1=1.2, b=0.75$) and LM Dirichlet ($\mu=2000$).
- Query Expansion: Curated Indonesian tourism synonym dictionary ($\ge 15$ pairs) with 5 verified query demonstrations.
- Rocchio Relevance Feedback: Interactive term-vector adjustments ($\alpha=1.0, \beta=0.75, \gamma=0.15$) generating boosted Elasticsearch queries.
- IR Evaluation: Manual binary ground truth (`qrels.csv`) across $\ge 10$ test queries computing Precision@10, Recall, F1-Score, and MAP across all three model configurations.
- Single-command reproducibility: `docker compose up --build` must spin up all three services without host dependency friction.

## Review Focus

1. **Text Deduplication Threshold Sensitivity**: Documents with identical structure but slight CMS metadata differences (e.g., author/date timestamps) must be deduplicated based on body content similarity $>95\%$, ensuring exact duplicate checks (MD5) and near-duplicate checks (Jaccard) do not discard distinct articles from the same portal.
2. **PySastrawi Domain Term Preservation**: Sastrawi stemming must not corrupt compound geographical terms, names of regions, or whitelisted tourism nouns (e.g., `curug`, `candi`, `pantai`, `danau`, `puncak`) into invalid or non-retrievable tokens.
3. **Elasticsearch Term Vectors Availability**: The `wisata_custom` index mapping must explicitly set `"term_vector": "with_positions_offsets_payloads"` on content fields; otherwise, Lucene will fail to return term vectors for posting list inspection and Rocchio feedback calculations.
4. **Zero-Result Handling in Rocchio Refinement**: When user relevance feedback produces terms with negative or negligible net weights, the Rocchio engine must preserve the original query terms to avoid empty or corrupted search results.
5. **Portability & Docker Healthcheck Ordering**: The backend service must wait for Elasticsearch to report healthy via container healthcheck before initializing index mappings or attempting document ingestion.

---

### Task 1: Repository Foundation, Collaboration Workflow, & Quality Gate

**Files:**
- Create: `docs/TEAM_WORKFLOW.md`
- Create: `docs/PROGRESS.md`
- Create: `AGENTS.md`
- Create: `Makefile`
- Create: `.gitignore`
- Create: `requirements.txt`
- Create: `scripts/verify_pipeline.py`

**Interfaces:**
- Consumes: None (root configuration)
- Produces: Collaboration rules for 3 members, living progress tracker, automated 7-gate validation script (`python3 scripts/verify_pipeline.py` or `make verify`).

- [ ] **Step 1: Write the failing test for project structure validation**

Create `tests/test_scaffolding.py`:
```python
import os

def test_project_structure_exists():
    required_paths = [
        "docs/TEAM_WORKFLOW.md",
        "docs/PROGRESS.md",
        "AGENTS.md",
        "requirements.txt",
        "Makefile",
        "scripts/verify_pipeline.py"
    ]
    for path in required_paths:
        assert os.path.exists(path), f"Required file missing: {path}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_scaffolding.py -v`
Expected: FAIL with missing paths.

- [ ] **Step 3: Implement root configuration and living documents**

- Create `.gitignore` (ignoring `.venv`, `__pycache__`, `node_modules`, `.es_data`, `.DS_Store`).
- Create `requirements.txt` with core dependencies: `fastapi>=0.110.0`, `uvicorn>=0.28.0`, `elasticsearch>=8.13.0`, `PySastrawi>=1.2.0`, `pydantic>=2.6.0`, `pytest>=8.0.0`, `beautifulsoup4>=4.12.0`, `requests>=2.31.0`.
- Create `docs/TEAM_WORKFLOW.md`: Define branch conventions (`main`, `feature/core-ir-engine`, `feature/frontend-ui`, `feature/crawler-data`, `docs/academic-report`), directory ownership (Member 1 = `frontend/`, Member 2 = `backend/`, Member 3 = `crawler/`, `docs/report/`), and PR protocols.
- Create `docs/PROGRESS.md`: Checkbox-based tracker for all 10 UAS evaluation components with component status table.
- Create `AGENTS.md`: Mandatory session start protocol, boundary enforcement, Clean Text Policy, and pre-commit checks.
- Create `scripts/verify_pipeline.py`: Automated CLI script testing directory integrity, Clean Text Policy compliance, and mock evaluation.
- Create `Makefile`: Exposing `make run`, `make test`, `make verify`, `make lint`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_scaffolding.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add .gitignore requirements.txt Makefile docs/ AGENTS.md scripts/ tests/test_scaffolding.py
git commit -m "chore(scaffold): initialize repository governance, team workflow, and quality gate"
```

---

### Task 2: Data Engineering & Crawler Spiders (Member 3 Lead)

**Files:**
- Create: `crawler/__init__.py`
- Create: `crawler/spiders/__init__.py`
- Create: `crawler/spiders/base_spider.py`
- Create: `crawler/spiders/nativeindonesia.py`
- Create: `crawler/spiders/indonesiatravel.py`
- Create: `crawler/spiders/wisato.py`
- Create: `crawler/run_crawler.py`
- Create: `data/raw/corpus_raw.json`
- Create: `data/raw/corpus_raw.csv`
- Test: `tests/test_crawler.py`

**Interfaces:**
- Consumes: None
- Produces: Raw crawled articles stored in `data/raw/corpus_raw.json` and `corpus_raw.csv` with schema: `doc_id`, `title`, `content`, `url`, `source`, `location`, `category`.

- [ ] **Step 1: Write the failing test for raw corpus schema & minimum volume**

Create `tests/test_crawler.py`:
```python
import json
import os

def test_raw_corpus_schema():
    corpus_path = "data/raw/corpus_raw.json"
    assert os.path.exists(corpus_path), "Raw corpus file missing"
    with open(corpus_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) >= 600, f"Expected >= 600 raw documents, found {len(data)}"
    required_keys = {"doc_id", "title", "content", "url", "source", "location", "category"}
    for doc in data[:20]:
        assert required_keys.issubset(doc.keys()), f"Missing keys in doc: {doc.get('doc_id')}"
        assert len(doc["title"].strip()) > 5, "Title too short"
        assert len(doc["content"].strip()) > 100, "Content too short"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_crawler.py -v`
Expected: FAIL with missing raw corpus file.

- [ ] **Step 3: Implement modular spiders & crawler execution script**

- Implement `BaseSpider` in `crawler/spiders/base_spider.py` defining standardized fetch with polite user-agent, error handling, rate limiting (0.5s delay), and HTML tag extraction.
- Implement `NativeIndonesiaSpider` in `crawler/spiders/nativeindonesia.py` targeting destination reviews (waterfalls, beaches, mountains).
- Implement `IndonesiaTravelSpider` in `crawler/spiders/indonesiatravel.py` targeting Indonesian Ministry of Tourism destination articles.
- Implement `WisatoSpider` in `crawler/spiders/wisato.py` targeting tourism guides and travel spotlights.
- Implement `crawler/run_crawler.py` executing all spiders with progress logging and saving outputs to `data/raw/corpus_raw.json` and `data/raw/corpus_raw.csv`.
- Execute crawler or ingestion runner to collect 600 to 800 comprehensive Indonesian travel articles.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_crawler.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add crawler/ data/raw/ tests/test_crawler.py
git commit -m "feat(crawler): implement multi-source travel spiders and collect raw corpus"
```

---

### Task 3: Text Deduplication Pipeline & Verification Report (Member 3 Lead)

**Files:**
- Create: `scripts/check_duplicates.py`
- Create: `data/processed/corpus_clean.json`
- Create: `data/processed/corpus_clean.csv`
- Create: `docs/evidence/duplicate_report.md`
- Test: `tests/test_deduplication.py`

**Interfaces:**
- Consumes: `data/raw/corpus_raw.json`
- Produces: `data/processed/corpus_clean.json` ($\ge 500$ unique documents) and formal verification report `docs/evidence/duplicate_report.md`.

- [ ] **Step 1: Write the failing test for deduplication logic & clean corpus count**

Create `tests/test_deduplication.py`:
```python
import json
import os
from scripts.check_duplicates import compute_similarity, deduplicate_corpus

def test_compute_similarity_exact_and_near():
    text1 = "pantai kuta bali merupakan destinasi wisata populer dengan pasir putih"
    text2 = "pantai kuta bali merupakan destinasi wisata populer dengan pasir putih"
    text3 = "curug leuwi hejo bogor air terjun alami jernih dan sejuk"
    assert compute_similarity(text1, text2) >= 0.99
    assert compute_similarity(text1, text3) < 0.30

def test_clean_corpus_minimum_unique():
    clean_path = "data/processed/corpus_clean.json"
    assert os.path.exists(clean_path), "Clean corpus missing"
    with open(clean_path, "r", encoding="utf-8") as f:
        clean_docs = json.load(f)
    assert len(clean_docs) >= 500, f"Expected >= 500 unique docs, found {len(clean_docs)}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_deduplication.py -v`
Expected: FAIL with `check_duplicates` missing or clean corpus missing.

- [ ] **Step 3: Implement `scripts/check_duplicates.py` and generate clean corpus**

- Implement exact hash matching (SHA-256) on normalized text.
- Implement near-duplicate detection using character 5-gram Jaccard Similarity and token overlap with threshold $\ge 0.95$.
- Filter out duplicate documents, keeping the primary most complete article.
- Output clean documents to `data/processed/corpus_clean.json` and `data/processed/corpus_clean.csv`.
- Write detailed log to `docs/evidence/duplicate_report.md` showing: Initial document count, number of exact duplicates removed, number of near-duplicates ($>95\%$) removed, and final unique count ($\ge 500$).

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_deduplication.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/check_duplicates.py data/processed/ docs/evidence/duplicate_report.md tests/test_deduplication.py
git commit -m "feat(data): implement duplicate checking pipeline and generate clean corpus"
```

---

### Task 4: Custom Preprocessing Pipeline (Member 2 / User Lead)

**Files:**
- Create: `backend/app/engine/preprocessor.py`
- Test: `tests/test_preprocessor.py`

**Interfaces:**
- Consumes: Raw text strings from crawled documents or incoming search queries.
- Produces: `preprocess_text(text: str) -> str` (space-delimited stemmed tokens), `inspect_preprocessing(text: str) -> dict` (structured comparison before/after).

- [ ] **Step 1: Write the failing test for custom domain cleaning, stopwords, and Sastrawi stemming**

Create `tests/test_preprocessor.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_preprocessor.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'backend.app.engine.preprocessor'`

- [ ] **Step 3: Implement `backend/app/engine/preprocessor.py`**

- Initialize `PySastrawi.Stemmer.StemmerFactory` singleton to avoid repeated instantiation overhead.
- Compile regex patterns for HTML stripping, emoji removal, price sanitization (`r'rp\s*[\d\.,]+'`, etc.), operational hours, and non-alphanumeric characters.
- Curate travel domain stopword set (merging Sastrawi stopwords with blog noise terms: `baca`, `klik`, `sumber`, `foto`, `artikel`, `penulis`, `instagram`, `detik`, `kompas`, `wisatawan`, `berkunjung`, `lokasi`, `berada`, `terletak`).
- Define explicit whitelist preserving core tourism terms (`pantai`, `curug`, `candi`, `danau`, `puncak`, `goa`, `hutan`, `taman`, `rute`, `tiket`, `pulau`, `air`, `terjun`, `gunung`, `desa`, `wisata`).
- Implement `preprocess_text(text: str) -> str`: runs case folding, cleaning regex, tokenization, stopword filtering, Sastrawi stemming, and returns space-joined tokens.
- Implement `inspect_preprocessing(text: str) -> dict`: returns step-by-step token streams for GUI inspector and report tables.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_preprocessor.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/engine/preprocessor.py tests/test_preprocessor.py
git commit -m "feat(engine): implement custom travel preprocessing pipeline with Sastrawi stemmer"
```

---

### Task 5: Dual-Index Elasticsearch Setup & Posting List Inspector (Member 2 / User Lead)

**Files:**
- Create: `docker-compose.yml`
- Create: `backend/app/engine/indexer.py`
- Test: `tests/test_indexer.py`

**Interfaces:**
- Consumes: `data/processed/corpus_clean.json`, clean documents.
- Produces: `create_indexes(es_client)`, `index_documents(es_client, docs)`, `get_posting_list(es_client, index_name, term) -> dict`.

- [ ] **Step 1: Write the failing test for dual-index creation and document indexing**

Create `tests/test_indexer.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_indexer.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'backend.app.engine.indexer'`

- [ ] **Step 3: Implement `docker-compose.yml` and `backend/app/engine/indexer.py`**

- Author root `docker-compose.yml` defining the `elasticsearch:8.13.4` service with single-node discovery, disabled security, 1.5GB memory limit, and healthcheck.
- In `backend/app/engine/indexer.py`:
  - Define schema mappings for `wisata_custom` (using `whitespace` analyzer for preprocessed fields, term vectors enabled, and both `custom_bm25` ($k_1=1.2, b=0.75$) and `custom_lm_dirichlet` ($\mu=2000$) configured).
  - Define schema mappings for `wisata_baseline` (using default `standard` analyzer and default BM25).
  - Implement `create_indexes(es_client)`: idempotently checks and creates both indexes.
  - Implement `build_bulk_actions(docs)` and `index_documents(es_client, docs)` using `elasticsearch.helpers.bulk`.
  - Implement `get_posting_list(es_client, index_name, term) -> dict`: queries the Elasticsearch `_termvectors` API or Lucene terms API to retrieve $df$, $tf$, and matching document IDs for posting list inspection.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_indexer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml backend/app/engine/indexer.py tests/test_indexer.py
git commit -m "feat(engine): implement dual-index Elasticsearch mappings and posting list inspector"
```

---

### Task 6: Ranked Retrieval Models (BM25 & LM Dirichlet + Baseline) (Member 2 / User Lead)

**Files:**
- Create: `backend/app/engine/searcher.py`
- Test: `tests/test_searcher.py`

**Interfaces:**
- Consumes: Preprocessed query, Elasticsearch client.
- Produces: `search_documents(es_client, query: str, model: str, top_k: int = 10) -> dict` returning ranked results, scores, execution latency, and snippet highlights.

- [ ] **Step 1: Write the failing test for retrieval query builders and response formatting**

Create `tests/test_searcher.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_searcher.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'backend.app.engine.searcher'`

- [ ] **Step 3: Implement `backend/app/engine/searcher.py`**

- Implement `build_search_query(query_text: str, model: str, top_k: int) -> dict`:
  - For `model="bm25"`: Targets `wisata_custom`, executes match/multi-match on `title_preprocessed` and `content_preprocessed` scored via BM25 similarity.
  - For `model="lm_dirichlet"`: Targets `wisata_custom` configured with LM Dirichlet similarity.
  - For `model="baseline"`: Targets `wisata_baseline`, runs on raw `title` and `content` using standard analyzer.
  - Configures Elasticsearch highlighting with `<em>` tags.
- Implement `search_documents(es_client, query: str, model: str, top_k: int = 10, preprocessed: bool = True) -> dict`:
  - Preprocesses incoming query if targeted at `wisata_custom`.
  - Measures server execution latency in milliseconds.
  - Formats ranked hits with rank position, relevance score, title, snippet, metadata badges, and URL.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_searcher.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/engine/searcher.py tests/test_searcher.py
git commit -m "feat(engine): implement BM25, LM Dirichlet, and baseline retrieval engine"
```

---

### Task 7: Query Expansion & Rocchio Relevance Feedback (Member 2 / User Lead)

**Files:**
- Create: `backend/app/engine/query_expansion.py`
- Create: `backend/app/engine/rocchio.py`
- Create: `docs/evidence/query_expansion_diff.md`
- Test: `tests/test_query_expansion.py`
- Test: `tests/test_rocchio.py`

**Interfaces:**
- Consumes: User query, document feedback IDs from frontend (`relevant_doc_ids`, `non_relevant_doc_ids`).
- Produces: `expand_query(query: str) -> dict` (synonym expansion), `compute_rocchio_query(es_client, query: str, rel_ids: list, non_rel_ids: list, alpha: float, beta: float, gamma: float) -> dict` (boosted query body).

- [ ] **Step 1: Write the failing tests for synonym query expansion and Rocchio calculations**

Create `tests/test_query_expansion.py`:
```python
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
```

Create `tests/test_rocchio.py`:
```python
from backend.app.engine.rocchio import calculate_rocchio_weights

def test_calculate_rocchio_weights():
    query_vector = {"pantai": 1.0, "bali": 1.0}
    rel_vectors = [{"pantai": 3.0, "pasir": 2.0, "putih": 2.0}]
    non_rel_vectors = [{"hotel": 4.0, "villa": 2.0}]
    
    weights = calculate_rocchio_weights(
        query_vec=query_vector,
        rel_vecs=rel_vectors,
        non_rel_vecs=non_rel_vectors,
        alpha=1.0,
        beta=0.75,
        gamma=0.15
    )
    # Target relevant terms should have positive adjusted weights
    assert weights["pantai"] > 1.0
    assert weights.get("pasir", 0) > 0
    # Negative term should be penalized or zeroed out
    assert weights.get("hotel", 0) <= 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_query_expansion.py tests/test_rocchio.py -v`
Expected: FAIL with missing modules.

- [ ] **Step 3: Implement Query Expansion & Rocchio Feedback Engine**

- In `backend/app/engine/query_expansion.py`:
  - Define Indonesian tourism dictionary containing $\ge 15$ bidirectional synonym pairs.
  - Implement `expand_query(query: str) -> dict`: detects matching terms, appends domain synonyms without duplicating, and returns original vs expanded comparison.
  - Generate verification table of 5 sample queries in `docs/evidence/query_expansion_diff.md`.
- In `backend/app/engine/rocchio.py`:
  - Implement `fetch_term_vectors(es_client, index_name, doc_ids) -> list[dict]`: reads normalized TF-IDF term vectors via Elasticsearch `_termvectors`.
  - Implement `calculate_rocchio_weights(query_vec, rel_vecs, non_rel_vecs, alpha=1.0, beta=0.75, gamma=0.15) -> dict`: computes $Q' = \alpha \vec{Q} + \beta \frac{1}{|D_r|} \sum \vec{D_r} - \gamma \frac{1}{|D_{nr}|} \sum \vec{D_{nr}}$.
  - Implement `build_rocchio_elasticsearch_query(base_query: str, weights: dict, top_k: int = 10) -> dict`: filters top positive terms and synthesizes a boosted Elasticsearch `bool` query with individual term weights mapped to `boost` values.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_query_expansion.py tests/test_rocchio.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/engine/query_expansion.py backend/app/engine/rocchio.py docs/evidence/query_expansion_diff.md tests/test_query_expansion.py tests/test_rocchio.py
git commit -m "feat(engine): implement synonym query expansion and Rocchio relevance feedback"
```

---

### Task 8: Ground Truth Dataset & Automated Evaluation Engine (Member 3 Lead)

**Files:**
- Create: `data/ground_truth/queries.json`
- Create: `data/ground_truth/qrels.csv`
- Create: `backend/app/engine/evaluator.py`
- Create: `data/ground_truth/evaluation_results.json`
- Test: `tests/test_evaluator.py`

**Interfaces:**
- Consumes: Test queries (`queries.json`), binary relevance judgments (`qrels.csv`), Elasticsearch retrieval engine.
- Produces: Precision@10, Recall, F1-Score, and MAP metrics across BM25 Custom, LM Dirichlet Custom, and Baseline StandardAnalyzer saved to `evaluation_results.json`.

- [ ] **Step 1: Write the failing test for IR evaluation metrics calculation**

Create `tests/test_evaluator.py`:
```python
from backend.app.engine.evaluator import (
    compute_precision_at_k,
    compute_recall,
    compute_f1,
    compute_average_precision,
    evaluate_retrieval_run
)

def test_metric_calculations():
    retrieved = ["doc_1", "doc_2", "doc_3", "doc_4", "doc_5", "doc_6", "doc_7", "doc_8", "doc_9", "doc_10"]
    relevant = {"doc_1", "doc_3", "doc_5", "doc_12", "doc_15"}  # 5 total relevant in collection
    
    p10 = compute_precision_at_k(retrieved, relevant, k=10)
    assert p10 == 0.3  # 3 out of 10 retrieved are relevant
    
    rec = compute_recall(retrieved, relevant)
    assert rec == 0.6  # 3 out of 5 relevant were retrieved
    
    f1 = compute_f1(p10, rec)
    assert round(f1, 4) == 0.4000
    
    ap = compute_average_precision(retrieved, relevant)
    # Positions: 1 (1/1), 3 (2/3), 5 (3/5) -> (1.0 + 0.6667 + 0.6) / 5 = 0.4533
    assert ap > 0.40 and ap < 0.50
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_evaluator.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'backend.app.engine.evaluator'`

- [ ] **Step 3: Implement Ground Truth Dataset & Evaluation Engine**

- In `data/ground_truth/queries.json`: Define 10 to 15 travel queries representing diverse intents (e.g., `wisata pantai pasir putih`, `air terjun curug bogor alami`, `candi peninggalan mataram kuno`, `snorkeling terumbu karang bali`, `pendakian gunung pemula`, `desa wisata adat sumatera`, `danau vulkanik sumatera utara`, `taman nasional konservasi satwa`, `spot kuliner legendaris jogja`, `wisata bahari kepulauan seribu`).
- In `data/ground_truth/qrels.csv`: Author binary ground truth (`query_id,doc_id,relevance`) with 0 or 1 annotations based on article contents.
- In `backend/app/engine/evaluator.py`:
  - Implement mathematical evaluation functions: `compute_precision_at_k`, `compute_recall`, `compute_f1`, and `compute_average_precision`.
  - Implement `run_full_evaluation(es_client) -> dict`: runs all test queries across `wisata_custom` (BM25), `wisata_custom` (LM Dirichlet), and `wisata_baseline` (StandardAnalyzer BM25), compiling the benchmark matrix.
  - Save full benchmark to `data/ground_truth/evaluation_results.json`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_evaluator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add data/ground_truth/ backend/app/engine/evaluator.py tests/test_evaluator.py
git commit -m "feat(evaluation): implement ground truth dataset and automated IR evaluator"
```

---

### Task 9: FastAPI Backend REST API (Member 2 / User Lead)

**Files:**
- Create: `backend/app/__init__.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/schemas.py`
- Create: `backend/app/api/routes.py`
- Create: `backend/app/main.py`
- Create: `backend/Dockerfile`
- Test: `tests/test_api.py`

**Interfaces:**
- Consumes: Core IR engine modules (`preprocessor`, `indexer`, `searcher`, `query_expansion`, `rocchio`, `evaluator`).
- Produces: REST API endpoints:
  - `GET /api/search?q={query}&model={bm25|lm_dirichlet|baseline}&expand={bool}&top_k={int}`
  - `POST /api/feedback/rocchio` (request body with query and relevant/non-relevant IDs)
  - `GET /api/inspect/preprocessing?text={text}`
  - `GET /api/inspect/posting-list?term={term}`
  - `GET /api/evaluation`
  - `GET /api/health`

- [ ] **Step 1: Write the failing test for FastAPI API endpoints**

Create `tests/test_api.py`:
```python
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@patch("backend.app.api.routes.get_es_client")
def test_search_endpoint(mock_get_es):
    mock_es = MagicMock()
    mock_get_es.return_value = mock_es
    with patch("backend.app.api.routes.search_documents") as mock_search:
        mock_search.return_value = {
            "query": "pantai bali",
            "model": "bm25",
            "latency_ms": 15.2,
            "total_hits": 1,
            "results": [{"rank": 1, "score": 10.5, "title": "Pantai Kuta", "url": "https://example.com"}]
        }
        response = client.get("/api/search?q=pantai+bali&model=bm25")
        assert response.status_code == 200
        data = response.json()
        assert data["total_hits"] == 1
        assert len(data["results"]) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_api.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'backend.app.main'`

- [ ] **Step 3: Implement schemas, routes, and FastAPI application**

- In `backend/app/api/schemas.py`: Define Pydantic request/response models (`SearchResponse`, `SearchResultItem`, `RocchioFeedbackRequest`, `PostingListResponse`, `EvaluationResponse`).
- In `backend/app/api/routes.py`:
  - Wire search route supporting single model and dual query execution for side-by-side view.
  - Wire Rocchio feedback route executing term-vector reweighting.
  - Wire preprocessing inspection and posting list inspection routes.
  - Wire evaluation benchmark route returning computed evaluation results.
- In `backend/app/main.py`: Instantiate FastAPI app with CORS middleware (allowing frontend port 3000), lifespan context for Elasticsearch connection management, and router inclusion under `/api`.
- In `backend/Dockerfile`: Define Python 3.11-slim container installing dependencies, copying application code, and serving with Uvicorn on port 8000.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_api.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/ backend/Dockerfile tests/test_api.py
git commit -m "feat(api): implement FastAPI REST API endpoints and backend Dockerfile"
```

---

### Task 10: Frontend Search Interface & Side-by-Side Split View (Member 1 Lead)

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/index.css`
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/App.jsx`
- Create: `frontend/src/services/api.js`
- Create: `frontend/src/components/SearchBar.jsx`
- Create: `frontend/src/components/ResultCard.jsx`
- Create: `frontend/src/components/SplitView.jsx`
- Create: `frontend/src/pages/SearchPage.jsx`
- Create: `frontend/Dockerfile`

**Interfaces:**
- Consumes: Backend REST API (`/api/search`, `/api/feedback/rocchio`).
- Produces: Complete search web application on port 3000 with real-time query inputs, suggestion pills, side-by-side algorithmic split comparison, keyword highlighting, and interactive feedback checkboxes.

- [ ] **Step 1: Scaffold Vite + React + Tailwind CSS frontend**

Set up `frontend/package.json` with dependencies: `react`, `react-dom`, `lucide-react`, `recharts`, `axios`, `clsx`, `tailwind-merge`, and dev dependencies: `vite`, `@vitejs/plugin-react`, `tailwindcss`, `autoprefixer`, `postcss`.

- [ ] **Step 2: Implement API client and search components**

- Implement `frontend/src/services/api.js`: Axios client wrapping `/api/search`, `/api/feedback/rocchio`, `/api/inspect`, and `/api/evaluation`.
- Implement `frontend/src/components/SearchBar.jsx`: Modern search bar with suggestion pills (`Wisata Pantai Bali`, `Curug di Bogor`, `Candi Borobudur Magelang`, `Snorkeling Raja Ampat`, `Desa Adat Toraja`), query expansion toggle, and model selector tabs.
- Implement `frontend/src/components/ResultCard.jsx`: Displays rank, relevance score, latency badge, portal source badges (`NativeIndonesia`, `IndonesiaTravel`, `Wisato`), snippet keyword highlighting, and interactive `[+ Relevan]` / `[- Tidak Relevan]` buttons.
- Implement `frontend/src/components/SplitView.jsx`: Two-column layout rendering Model 1 (BM25) and Model 2 (LM Dirichlet / Baseline) side-by-side for classroom demonstration.
- Implement `frontend/src/pages/SearchPage.jsx`: Orchestrates search state, query expansion chips, side-by-side toggles, and Rocchio action bar.
- Author `frontend/Dockerfile` building the React app with Node.js 20 and serving with Nginx or Vite preview on port 3000.

- [ ] **Step 3: Verify frontend build & interface rendering**

Run: `cd frontend && npm install && npm run build`
Expected: Clean build without errors, producing `frontend/dist/`.

- [ ] **Step 4: Commit**

```bash
git add frontend/
git commit -m "feat(frontend): build React search interface with side-by-side split view and feedback controls"
```

---

### Task 11: Frontend Analytics Dashboard & Inspector Modal (Member 1 Lead)

**Files:**
- Create: `frontend/src/components/InspectorModal.jsx`
- Create: `frontend/src/components/EvaluationCharts.jsx`
- Create: `frontend/src/pages/DashboardPage.jsx`
- Modify: `frontend/src/App.jsx`

**Interfaces:**
- Consumes: Backend REST API (`/api/evaluation`, `/api/inspect/preprocessing`, `/api/inspect/posting-list`).
- Produces: Comprehensive analytics dashboard with Recharts visualizations, evaluation comparison tables, and posting list inspector modal.

- [ ] **Step 1: Implement posting list and preprocessing inspector modal**

- Implement `frontend/src/components/InspectorModal.jsx`: Modal allowing users to enter a sample travel text to view side-by-side token transformations (before vs after Sastrawi stemming), or enter a term (`curug`, `pantai`, `candi`) to inspect its Lucene posting list ($df$, $tf$, matching doc IDs).

- [ ] **Step 2: Implement evaluation dashboard and charts**

- Implement `frontend/src/components/EvaluationCharts.jsx`: Using Recharts to build:
  - Grouped Bar Chart comparing Precision@10, Recall, F1-Score, and MAP across BM25 Custom, LM Dirichlet Custom, and Baseline StandardAnalyzer.
  - Radar Chart visualizing overall balance of retrieval qualities.
- Implement `frontend/src/pages/DashboardPage.jsx`:
  - Renders the comparative benchmark table required by course specifications.
  - Renders per-query evaluation breakdown table with ground-truth relevance matching.
- Update `frontend/src/App.jsx`: Add header navigation between "Pencarian (Search)" and "Dashboard Evaluasi (Analytics)".

- [ ] **Step 3: Verify frontend build with dashboard**

Run: `cd frontend && npm run build`
Expected: Build passes with zero warnings or errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/InspectorModal.jsx frontend/src/components/EvaluationCharts.jsx frontend/src/pages/DashboardPage.jsx frontend/src/App.jsx
git commit -m "feat(frontend): implement evaluation analytics dashboard and posting list inspector modal"
```

---

### Task 12: Final Docker Orchestration, Academic Documentation, & End-to-End Verification (All Members)

**Files:**
- Modify: `docker-compose.yml`
- Create: `README.md`
- Create: `docs/report/LAPORAN_DRAFT.md`
- Create: `docs/slides/SLIDES_OUTLINE.md`
- Create: `docs/evidence/posting_list_sample.md`
- Create: `docs/evidence/rocchio_demo.md`
- Modify: `docs/PROGRESS.md`
- Test: `scripts/verify_pipeline.py`

**Interfaces:**
- Consumes: All completed frontend, backend, data, and crawler components.
- Produces: 100% complete repository meeting all course submission criteria, fully passing `make verify` pre-flight gate.

- [ ] **Step 1: Write integration test for full Docker Compose service definitions**

Update `tests/test_scaffolding.py` to assert that all required deliverables exist:
```python
def test_all_deliverables_present():
    required = [
        "data/raw/corpus_raw.json",
        "data/processed/corpus_clean.json",
        "docs/evidence/duplicate_report.md",
        "docs/evidence/query_expansion_diff.md",
        "docs/evidence/posting_list_sample.md",
        "docs/evidence/rocchio_demo.md",
        "README.md",
        "requirements.txt",
        "docker-compose.yml"
    ]
    for path in required:
        assert os.path.exists(path), f"Missing final deliverable: {path}"
```

- [ ] **Step 2: Finalize Docker Compose, README, report, and slide templates**

- In `docker-compose.yml`: Wire `elasticsearch`, `backend`, and `frontend` with healthchecks, environment variables, and network bridges.
- In `README.md`: Document team members (Kelompok 10), project overview, architecture diagram, dependencies, single-command run instructions (`docker compose up --build`), local development instructions, and sample test queries with results.
- In `docs/evidence/`: Author `posting_list_sample.md` (sample Lucene posting lists) and `rocchio_demo.md` (relevance feedback demonstration logs).
- In `docs/report/LAPORAN_DRAFT.md`: Structure formal report draft adhering to USK FMIPA thesis format (Bab I Pendahuluan, Bab II Tinjauan Pustaka, Bab III Metodologi & Arsitektur, Bab IV Hasil Evaluasi & Pembahasan, Bab V Kesimpulan, Lampiran Pembagian Tugas Kelompok 10).
- In `docs/slides/SLIDES_OUTLINE.md`: Structure complete presentation slide deck for 5-minute live demo.
- In `docs/PROGRESS.md`: Update all task checkboxes to complete (`- [x]`).

- [ ] **Step 3: Execute full pipeline pre-flight verification**

Run: `python3 scripts/verify_pipeline.py`
Expected: All 7 quality gates report `[PASS]`.
Run: `pytest tests/ -v`
Expected: 100% automated tests green.

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml README.md docs/ tests/ scripts/
git commit -m "docs: complete academic report draft, presentation outline, and end-to-end delivery verification"
```




