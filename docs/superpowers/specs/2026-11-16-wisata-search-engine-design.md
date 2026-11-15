# Architectural Design Specification: Indonesian Tourism Vertical Search Engine

- **Project**: Vertical Search Engine for Indonesian Tourism Articles & Destination Reviews (`mesin-pencari-wisata-nusantara`)
- **Course**: Praktikum Penelusuran Informasi (Information Retrieval Lab)
- **Institution**: Universitas Syiah Kuala (USK) - FMIPA
- **Team Size**: 3 Members
- **Date**: 2026-11-16
- **Status**: Draft for Review

---

## 1. Executive Summary & Goals

The objective of this project is to build an end-to-end Indonesian Vertical Search Engine specialized in Indonesian archipelago tourism articles, destination guides, and cultural travel reviews (**Artikel Wisata Nusantara**). The system operates on a freshly crawled corpus of at least 500 unique Indonesian travel documents, implements a domain-adapted Indonesian text preprocessing pipeline, and indexes documents into **Elasticsearch (Apache Lucene)** using an isolated dual-index architecture. 

The search engine compares two ranked retrieval models from distinct similarity families (**Okapi BM25** and **Language Modeling with Bayesian Dirichlet Smoothing (LM Dirichlet)**), evaluated against a **StandardAnalyzer baseline**. The system also implements a domain-specific **Query Expansion** module (15+ synonym pairs) and an interactive **Rocchio Relevance Feedback** algorithm using document term vectors. An interactive **React + Vite + Tailwind CSS** web application provides real-time search, side-by-side algorithmic split comparison, keyword snippet highlighting, and an evaluation metrics dashboard. The entire application is containerized with **Docker Compose** for seamless, single-command portability.

### Key Success Criteria:
1. **Corpus Quality & Scale**: Crawl 600 to 800 Indonesian tourism articles across multiple established travel portals (**NativeIndonesia.com**, **Indonesia.travel**, and **Wisato.id**). Ensure at least 500 unique documents remain after rigorous text deduplication (>95% similarity threshold).
2. **Custom Domain Preprocessing**: A tailored pipeline featuring domain cleaning (sanitizing ticket prices, operational hours, HTML, emojis), custom travel stopwords, and **PySastrawi** Indonesian morphological stemming. Integrated into Lucene as pre-tokenized fields indexed with `WhitespaceAnalyzer`.
3. **Dual Ranked Retrieval Models**:
   - Probabilistic Lexical: **Okapi BM25** ($k_1=1.2, b=0.75$).
   - Language Modeling: **LM Dirichlet** ($\mu=2000$).
   - Baseline: BM25 on raw text indexed with Lucene's default **StandardAnalyzer**.
4. **Lucene Introspection & Inverted Index Verification**: Script and GUI extraction of posting lists ($tf$, $df$, document pointers) for key tourism terms.
5. **Query Expansion & Relevance Feedback**:
   - Indonesian tourism synonym dictionary with $\ge 15$ pairs; verified with 5 sample queries before and after expansion.
   - Interactive **Rocchio Algorithm** ($\alpha=1.0, \beta=0.75, \gamma=0.15$) dynamically recalculating query term weights from user-selected relevant ($D_r$) and non-relevant ($D_{nr}$) documents via Elasticsearch `_termvectors`.
6. **Quantitative Evaluation**: Precision@10, Recall, F1-Score, and Mean Average Precision (MAP) evaluated against $\ge 10$ test queries annotated with manual ground-truth binary relevance judgments (0/1).
7. **Interactive Web UI**: Modern React frontend supporting side-by-side algorithm comparison, interactive relevance feedback checkboxes, and a Recharts analytics dashboard.
8. **Portability & Zero-Setup Delivery**: Single-command startup via `docker compose up --build` serving Elasticsearch, FastAPI backend, and React frontend.
9. **Academic Deliverables & Evidence**: Structured repository containing raw and clean corpora, deduplication evidence report, evaluation benchmark tables, presentation slides deck, and living team collaboration workflows.

## 2. System Architecture & Docker Containerization

The system follows a three-tier decoupled client-server architecture orchestrated via Docker Compose.

```
[ User / Evaluator / Lecturer / Lab Assistant ]
                       │
                       ▼ (Port 3000)
┌────────────────────────────────────────────────────────────────────────┐
│ Docker Environment (docker compose up --build)                         │
│                                                                        │
│  ┌─────────────────────────┐          ┌─────────────────────────────┐  │
│  │   Frontend Service      │          │     Backend API Service     │  │
│  │   (React 18 + Vite +    │─────────▶│     (Python 3.11 FastAPI    │  │
│  │    Tailwind CSS)        │   REST   │      + PySastrawi + ES py)  │  │
│  └─────────────────────────┘  Calls   └──────────────┬──────────────┘  │
│                                                      │                 │
│                                                      ▼ (Port 9200)     │
│                                       ┌─────────────────────────────┐  │
│                                       │    Elasticsearch Service    │  │
│                                       │    (Lucene IR Engine 8.x)   │  │
│                                       │ - wisata_custom (BM25 & LM) │  │
│                                       │ - wisata_baseline (Standard)│  │
│                                       └──────────────┬──────────────┘  │
│                                                      │                 │
│                                                      ▼                 │
│                                       ┌─────────────────────────────┐  │
│                                       │ Persistent Docker Volume    │  │
│                                       │ (es_data for Lucene indexes)│  │
│                                       └─────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Service Specifications
1. **`elasticsearch` Service**:
   - **Engine**: Elasticsearch 8.13.x (official Apache Lucene distribution).
   - **Configuration**: Single-node development cluster (`discovery.type=single-node`), memory limit 1.5 GB - 2.0 GB, security disabled (`xpack.security.enabled=false`) for lightweight internal local communication.
   - **Storage**: Persistent named volume `es_data` mounted at `/usr/share/elasticsearch/data` to ensure indexed documents persist across restarts.
   - **Port**: `9200` exposed for backend access and debugging.

2. **`backend` Service**:
   - **Runtime**: Python 3.11 with FastAPI, Uvicorn, and official `elasticsearch-py` client.
   - **Role**: Coordinates data ingestion, text preprocessing (PySastrawi), index management, retrieval queries, query expansion, Rocchio feedback computation, and automated evaluation metrics.
   - **Orchestration**: Configured with `depends_on: { elasticsearch: { condition: service_healthy } }` via container healthcheck.
   - **Port**: `8000` exposing REST endpoints.

3. **`frontend` Service**:
   - **Runtime**: Node.js 20 build stage, served in production via Nginx (or Vite preview server).
   - **Role**: Delivers the user interface, search interactions, side-by-side comparison view, relevance feedback triggers, and Recharts evaluation visualization.
   - **Port**: `3000` accessible via web browser.

---

## 3. Data Pipeline & Core IR Engine (Member 2 Lead)

Member 2 is the technical owner of the backend and Information Retrieval engine. All components are implemented in `backend/app/engine/` with comprehensive unit tests.

### 3.1 Text Preprocessing Pipeline (`backend/app/engine/preprocessor.py`)
1. **Case Folding & Cleaning**:
   - Convert all characters to lowercase.
   - Strip HTML tags (`<p>`, `<div>`, `<img>`, etc.) and residual script elements.
   - Strip emojis and decorative Unicode symbols.
   - Sanitize domain-specific patterns such as ticket pricing (e.g., `Rp 15.000`, `Rp.25.000,-`), operational hours (e.g., `08.00 - 17.00 WIB`), and generic phone/contact details that do not carry semantic relevance for tourism queries.
2. **Tokenization**:
   - Whitespace and regex tokenization into distinct Indonesian word tokens.
3. **Domain Stopword Removal**:
   - Standard Indonesian stopwords based on Sastrawi and Tala lexicons.
   - Augmented with travel blog noise words: `baca`, `klik`, `sumber`, `foto`, `artikel`, `penulis`, `instagram`, `detik`, `kompas`, `wisatawan`, `berkunjung`, `lokasi`, `berada`, `terletak`.
   - Explicit whitelist preserving essential tourism descriptors: `pantai`, `curug`, `candi`, `danau`, `puncak`, `goa`, `hutan`, `taman`, `rute`, `tiket`, `pulau`, `air`, `terjun`, `gunung`.
4. **Morphological Stemming**:
   - Apply **PySastrawi** (Nazief-Adriani algorithm) to reduce affixes (prefixes, suffixes, confixes) to root words.
5. **Introspection Utility**:
   - Export `inspect_preprocessing(raw_text)` function returning structured before-and-after side-by-side token streams for demonstration and report documentation.

### 3.2 Dual-Index Lucene Architecture (`backend/app/engine/indexer.py`)
To isolate and measure the exact impact of custom preprocessing versus standard indexing, Elasticsearch manages two distinct indexes:

1. **`wisata_custom` Index**:
   - **Content Field**: `content_preprocessed` and `title_preprocessed`.
   - **Analyzer**: `whitespace` analyzer (indexing tokens directly produced by the custom Python Sastrawi pipeline).
   - **Term Vectors**: `"term_vector": "with_positions_offsets_payloads"` enabled to support posting list inspection and Rocchio feedback.
   - **Configured Similarities**:
     - `custom_bm25`: Type `BM25`, $k_1 = 1.2$, $b = 0.75$.
     - `custom_lm_dirichlet`: Type `LMDirichlet`, $\mu = 2000$.

2. **`wisata_baseline` Index**:
   - **Content Field**: `content` and `title` (raw, unprocessed text).
   - **Analyzer**: Lucene default `standard` analyzer.
   - **Similarity**: Default Lucene BM25 similarity.
   - **Purpose**: Serves as the experimental control group required by course specifications.

### 3.3 Posting List Introspection (`get_posting_list(term)`)
- Provides an automated utility and API endpoint to inspect the inverted index posting list for any given term (e.g., `curug`, `pantai`, `candi`).
- Retrieves:
  - Document frequency ($df$): Total number of documents containing the term.
  - Term frequency ($tf$): Occurrences per document.
  - Document ID postings list.

### 3.4 Ranked Retrieval Models
1. **Model 1: Okapi BM25 (Probabilistic Model)**
   - Score formula:
     $$Score(D, Q) = \sum_{q \in Q} IDF(q) \cdot \frac{f(q, D) \cdot (k_1 + 1)}{f(q, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{avgdl}\right)}$$
     Where $IDF(q) = \ln \left( \frac{N - n(q) + 0.5}{n(q) + 0.5} + 1 \right)$, $k_1 = 1.2$, and $b = 0.75$.
2. **Model 2: LM Dirichlet (Language Modeling with Bayesian Smoothing)**
   - Score formula:
     $$Score(D, Q) = \sum_{q \in Q} \ln \left( 1 + \frac{f(q, D)}{\mu \cdot P(q|C)} \right) + |Q| \cdot \ln \left( \frac{\mu}{|D| + \mu} \right)$$
     Where $P(q|C) = \frac{cf(q)}{|C|}$ is the collection probability and $\mu = 2000$ is the Dirichlet smoothing parameter.
3. **Baseline Model: StandardAnalyzer BM25**
   - BM25 model executed against the `wisata_baseline` index to demonstrate the qualitative and quantitative benefits of custom Sastrawi preprocessing.

### 3.5 Query Expansion Module (`backend/app/engine/query_expansion.py`)
- Curated synonym dictionary containing $\ge 15$ pairs of Indonesian tourism terminology:
  - `curug` $\leftrightarrow$ `air terjun`
  - `pelesir` $\leftrightarrow$ `wisata`, `liburan`
  - `penginapan` $\leftrightarrow$ `hotel`, `homestay`, `resort`, `villa`
  - `bahari` $\leftrightarrow$ `laut`, `pantai`
  - `snorkeling` $\leftrightarrow$ `selam`
  - `candi` $\leftrightarrow$ `situs bersejarah`
  - `kuliner` $\leftrightarrow$ `makanan khas`
  - `kamping` $\leftrightarrow$ `berkemah`
  - `pendakian` $\leftrightarrow$ `trekking`, `mendaki`
  - `wahana` $\leftrightarrow$ `atraksi`
  - `souvenir` $\leftrightarrow$ `oleh-oleh`
  - `panorama` $\leftrightarrow$ `pemandangan`
  - `desa wisata` $\leftrightarrow$ `kampung adat`
  - `biota laut` $\leftrightarrow$ `terumbu karang`, `ikan`
  - `sunset` $\leftrightarrow$ `matahari terbit`, `senja`
- **Verification Suite**: Evaluates and outputs exact query strings before and after expansion for at least 5 verification queries (e.g., `curug bogor`, `wisata bahari lombok`, `penginapan dieng`).

### 3.6 Rocchio Relevance Feedback Engine (`backend/app/engine/rocchio.py`)
- Implements the classic vector space relevance feedback algorithm:
  $$Q' = \alpha \vec{Q} + \beta \frac{1}{|D_r|} \sum_{D \in D_r} \vec{D} - \gamma \frac{1}{|D_{nr}|} \sum_{D \in D_{nr}} \vec{D}$$
  With default tuning parameters: $\alpha = 1.0, \beta = 0.75, \gamma = 0.15$.
- **Workflow**:
  1. The user flags documents in the search result list as Relevant ($D_r$) or Non-Relevant ($D_{nr}$).
  2. Backend fetches exact term vectors for selected documents from Elasticsearch via the `_termvectors` API.
  3. Term weights are normalized and aggregated according to the Rocchio formula.
  4. Top positive-weighted expansion terms are extracted and synthesized into a modified Elasticsearch `bool` query with boosted `should` clauses.
  5. Updated ranked results are returned and compared against the initial unexpanded result set.

## 4. Frontend Search Interface (Member 1 Lead)

Member 1 is the technical owner of the user interface in `frontend/`. Built with **React 18 + Vite + Tailwind CSS + Lucide Icons + Recharts**, it serves both end-user search workflows and academic evaluation presentations.

### 4.1 Key Pages & Components
1. **Search & Exploration View (`frontend/src/pages/SearchPage.jsx`)**:
   - **Search Input Bar**: Responsive input with real-time suggestion pills (`Wisata Pantai Bali`, `Curug di Bogor`, `Candi Magelang`, `Snorkeling Raja Ampat`, `Desa Adat Toraja`).
   - **Model Selector**: Switch between Single Model view (`BM25`, `LM Dirichlet`, `Baseline Standard`) and **Side-by-Side Split View** (displaying two models simultaneously in adjacent columns).
   - **Query Expansion Toggle**: Checkbox triggering Indonesian tourism synonym expansion with visual before/after query diff chips.
2. **Search Result Card (`frontend/src/components/ResultCard.jsx`)**:
   - Document title, source portal badge (`NativeIndonesia`, `IndonesiaTravel`, `Wisato`), retrieval rank, score, execution latency in milliseconds, and original external URL.
   - Text snippet with matched keyword highlighting.
   - **Interactive Relevance Feedback Controls**: Individual `[+ Relevant]` and `[- Non-Relevant]` toggle buttons per document.
   - **Rocchio Action Bar**: Fixed bottom bar active when at least one document is tagged, triggering dynamic query refinement.
3. **Posting List & Preprocessing Inspector Modal (`frontend/src/components/InspectorModal.jsx`)**:
   - Demonstrates text transformations (raw text versus Sastrawi stemmed tokens).
   - Term postings list viewer querying Elasticsearch term vectors for live classroom demonstration.
4. **Evaluation Analytics Dashboard (`frontend/src/pages/DashboardPage.jsx`)**:
   - **Comparative Benchmark Table**: Displays side-by-side **Precision@10**, **Recall**, **F1-Score**, and **MAP** across all 3 configurations (BM25 Custom, LM Dirichlet Custom, and Baseline StandardAnalyzer).
   - **Interactive Charts (Recharts)**:
     - Grouped Bar Chart comparing metric scores across models.
     - Radar Chart displaying holistic balance across Precision, Recall, F1, and MAP.
   - **Per-Query Drilldown**: Interactive selector showing detailed rankings and relevance matches for each of the 10 ground-truth test queries.

---

## 5. Crawler, Deduplication, & IR Evaluation (Member 3 Lead)

Member 3 is the technical owner of data collection, text deduplication, ground-truth relevance annotation, and final academic report documentation.

### 5.1 Multi-Source Web Crawler (`crawler/`)
- **Target Volume**: 600 to 800 Indonesian travel documents to ensure a safe margin above the required 500 unique documents after deduplication.
- **Target Spiders**:
  1. `crawler/spiders/nativeindonesia.py`: ~300 comprehensive reviews of waterfalls (curug), beaches, hiking trails, and historical sites.
  2. `crawler/spiders/indonesiatravel.py`: ~250 official Indonesian Ministry of Tourism articles covering super-priority destinations and cultural heritage.
  3. `crawler/spiders/wisato.py`: ~200 travel articles detailing popular tourist destinations, local attractions, and amenities.
- **Document Schema**:
  ```json
  {
    "doc_id": "wisata_001",
    "title": "Pesona Keindahan Curug Leuwi Hejo Bogor",
    "content": "Curug Leuwi Hejo merupakan salah satu air terjun alami...",
    "url": "https://www.nativeindonesia.com/curug-leuwi-hejo/",
    "source": "nativeindonesia",
    "location": "Bogor, Jawa Barat",
    "category": "Wisata Alam"
  }
  ```

### 5.2 Text Deduplication Pipeline (`scripts/check_duplicates.py`)
- Sesuai ketentuan aslab: *"Duplikat (kemiripan teks >95%) wajib diperiksa dan dilaporkan."*
- **Detection Methodology**:
  1. **Exact Duplicate Check**: MD5 and SHA-256 hash comparison across normalized body text.
  2. **Near-Duplicate Check**: Character 5-gram Jaccard Similarity and TF-IDF Cosine Similarity. Any document pair exceeding a 0.95 similarity score is flagged as duplicate.
- **Deduplication Artifacts**:
  - `data/raw/corpus_raw.json` and `data/raw/corpus_raw.csv` (unfiltered crawled corpus).
  - `data/processed/corpus_clean.json` and `data/processed/corpus_clean.csv` (deduplicated corpus with $\ge 500$ unique documents).
  - `docs/evidence/duplicate_report.md`: Formal verification report logging initial document count, detected duplicates, pairwise similarity scores, and final unique count.

### 5.3 Ground Truth & Quantitative Evaluation Engine
1. **Test Queries (`data/ground_truth/queries.json`)**:
   - 10 to 15 distinct, representative queries spanning Indonesian tourism categories (e.g., beaches, waterfalls, mountain trekking, ancient temples, marine diving, traditional villages).
2. **Relevance Judgment Matrix (`data/ground_truth/qrels.csv`)**:
   - Manual binary annotation (1 = Relevant, 0 = Non-Relevant) performed by team members based on full article contents.
3. **Automated Evaluator (`backend/app/engine/evaluator.py`)**:
   - Executes all test queries across the three configurations:
     - Model 1: Okapi BM25 on `wisata_custom`
     - Model 2: LM Dirichlet on `wisata_custom`
     - Baseline: BM25 on `wisata_baseline`
   - Computes:
     - **Precision@10**: $\frac{|Retrieved_{10} \cap Relevant|}{10}$
     - **Recall**: $\frac{|Retrieved \cap Relevant|}{|Total Relevant|}$
     - **F1-Score**: $2 \cdot \frac{Precision \cdot Recall}{Precision + Recall}$
     - **MAP (Mean Average Precision)**: $\frac{1}{|Q|} \sum_{q=1}^{|Q|} AveP(q)$, where $AveP = \sum_{k=1}^{n} P(k) \cdot \Delta r(k)$
   - Saves results to `data/ground_truth/evaluation_results.json` for frontend rendering and report tables.

## 6. Team Collaboration, Git Strategy, & Living Artifacts

To prevent merge conflicts and ensure clear accountability across the 3 members, the repository establishes strict workspace isolation.

### 6.1 Member Responsibilities & Boundaries
```
┌────────────────────────────────────────────────────────────────────────┐
│ Member 1 (Frontend & UI Lead)                                          │
│ - Directory: frontend/                                                 │
│ - Deliverables: React Search UI, Split View, Recharts Dashboard,       │
│   Inspector Modals, Presentation Slides design                         │
├────────────────────────────────────────────────────────────────────────┤
│ Member 2 (Core IR Engine & Backend Lead - User)                        │
│ - Directory: backend/, docker-compose.yml                              │
│ - Deliverables: Preprocessing pipeline, Dual-Index Elasticsearch       │
│   setup, BM25 & LM Dirichlet models, Posting list inspector,           │
│   Query Expansion, Rocchio feedback engine, FastAPI REST endpoints     │
├────────────────────────────────────────────────────────────────────────┤
│ Member 3 (Data Engineering, Evaluator, & Report Lead)                  │
│ - Directory: crawler/, data/, docs/report/, docs/evidence/             │
│ - Deliverables: Multi-source spiders, Duplicate checking pipeline,     │
│   Test queries, Manual qrels ground truth, Academic report Bab I–V     │
└────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Living Documents & Governance
1. **`docs/TEAM_WORKFLOW.md`**:
   - Outlines branch conventions (`main`, `feature/core-ir-engine`, `feature/frontend-ui`, `feature/crawler-data`, `docs/academic-report`).
   - Defines directory access boundaries to prevent code conflicts.
   - Provides step-by-step local run and pull request guidelines.
2. **`docs/PROGRESS.md`**:
   - Living progress tracker tracking feature status with checkboxes (`- [ ]` / `- [x]`).
   - Serves as the central coordination dashboard for team meetings and status updates.
3. **`AGENTS.md`**:
   - Bootstrap protocol for AI coding assistants working in the repository.
   - Enforces directory boundaries, verification gates, and Clean Text Policy.

---

## 7. Repository Structure & Evidence Organization

```
mesin-pencari-wisata-nusantara/
├── backend/
│   ├── app/
│   │   ├── engine/
│   │   │   ├── preprocessor.py       # Sastrawi + domain cleaning
│   │   │   ├── indexer.py            # Dual-index manager & posting lists
│   │   │   ├── searcher.py           # BM25, LM Dirichlet, & Baseline execution
│   │   │   ├── query_expansion.py    # 15+ synonym pairs
│   │   │   ├── rocchio.py            # Relevance feedback with term vectors
│   │   │   └── evaluator.py          # Precision@10, Recall, F1, MAP calculator
│   │   ├── api/
│   │   │   ├── routes.py             # Search, feedback, inspection, metrics
│   │   │   └── schemas.py            # Pydantic data models
│   │   └── main.py                   # FastAPI application entrypoint
│   ├── tests/                        # Comprehensive pytest suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/               # SearchBar, ResultCard, SplitView, Inspector
│   │   ├── pages/                    # SearchPage, DashboardPage
│   │   ├── services/                 # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── Dockerfile
├── crawler/
│   ├── spiders/
│   │   ├── nativeindonesia.py
│   │   ├── indonesiatravel.py
│   │   └── wisato.py
│   └── run_crawler.py
├── data/
│   ├── raw/
│   │   ├── corpus_raw.json           # Crawled 600-800 documents
│   │   └── corpus_raw.csv
│   ├── processed/
│   │   ├── corpus_clean.json         # Deduplicated >= 500 documents
│   │   └── corpus_clean.csv
│   └── ground_truth/
│       ├── queries.json              # 10-15 test queries
│       ├── qrels.csv                 # Binary relevance judgments
│       └── evaluation_results.json   # Computed metrics
├── docs/
│   ├── evidence/                     # High-resolution screenshots & logs
│   │   ├── duplicate_report.md
│   │   ├── posting_list_sample.md
│   │   ├── query_expansion_diff.md
│   │   └── rocchio_demo.md
│   ├── report/                       # Final academic report
│   ├── slides/                       # Presentation deck
│   ├── TEAM_WORKFLOW.md              # Team git & collaboration guidelines
│   └── PROGRESS.md                   # Living task tracker
├── scripts/
│   ├── check_duplicates.py           # Hash & Jaccard >95% similarity
│   └── verify_pipeline.py            # Automated pre-flight quality check
├── docker-compose.yml                # Full stack container orchestration
├── Makefile                          # Unified project commands
├── requirements.txt                  # Python root dependencies
└── README.md                         # Project overview, installation, demo
```

---

## 8. Deliverables & Evaluation Rubric Mapping

Every requirement from the official course specification is mapped to verified project artifacts:

| Component | Rubric Weight | Deliverable Artifacts & Verification |
| :--- | :---: | :--- |
| **1. Korpus & Crawling** | 10% | `data/raw/corpus_raw.json` ($\ge 600$ articles), `data/processed/corpus_clean.json` ($\ge 500$ unique articles), `scripts/check_duplicates.py`, `docs/evidence/duplicate_report.md`. |
| **2. Custom Preprocessing** | 15% | `preprocessor.py` (HTML/emoji/price cleaning, travel stopwords, Sastrawi stemmer), WhitespaceAnalyzer integration, side-by-side text transformation diffs in UI and report. |
| **3. Indexing & 2 Model Retrieval** | 20% | Dual Elasticsearch indexes (`wisata_custom` vs `wisata_baseline`), BM25 ($k_1=1.2, b=0.75$) vs LM Dirichlet ($\mu=2000$), Baseline StandardAnalyzer, posting list inspector tool. |
| **4. Query Expansion & Rocchio** | 10% | `query_expansion.py` ($\ge 15$ synonym pairs, 5 verification queries), `rocchio.py` ($\alpha=1.0, \beta=0.75, \gamma=0.15$ with Elasticsearch `_termvectors`). |
| **5. Evaluasi Sistem** | 15% | $\ge 10$ test queries, manual binary relevance judgments (`qrels.csv`), automated evaluator computing Precision@10, Recall, F1, and MAP comparison table. |
| **6. Antarmuka Pencarian** | 10% | React 18 web UI, Side-by-Side comparison split view, keyword highlighting, source portal badges, interactive Rocchio feedback buttons, Recharts dashboard. |
| **7. Presentasi & Tanya Jawab** | 20% | Comprehensive slide deck (`docs/slides/`), live demo walkthrough script, well-documented `README.md` and `docs/TEAM_WORKFLOW.md`. |
| **Total** | **100%** | Comprehensive, end-to-end Indonesian Tourism Vertical Search Engine. |



