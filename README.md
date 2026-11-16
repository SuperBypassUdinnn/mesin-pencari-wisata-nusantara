# Indonesian Tourism Vertical Search Engine (Mesin Pencari Wisata Nusantara)

A containerized vertical search engine for Indonesian archipelago tourism articles and destination reviews, comparing probabilistic lexical retrieval (**Okapi BM25**) and language modeling retrieval (**LM Dirichlet**) against a Lucene **StandardAnalyzer baseline**.

Developed for the **Praktikum Penelusuran Informasi (Information Retrieval Lab)** course at **Universitas Syiah Kuala (USK) - FMIPA**.

- **Group**: Kelompok 10
- **Category**: Kategori 9 — Artikel Wisata Nusantara (Travel Blogs & Indonesian Tourism Portals)

---

## Team Members and Roles

| Member | Primary Role | Directory Workspace | Key Responsibilities |
| :--- | :--- | :--- | :--- |
| **Member 1** | Frontend & UI Lead | `frontend/`, `docs/slides/` | React 18 search UI, Side-by-Side Split View, keyword highlighting, relevance feedback controls, Recharts dashboard, presentation deck |
| **Member 2** | Core IR Engine & Backend Lead | `backend/`, `docker-compose.yml` | Indonesian preprocessing (PySastrawi), dual-index Elasticsearch mappings, BM25 & LM Dirichlet models, posting-list inspector, query expansion, Rocchio feedback engine, FastAPI REST API |
| **Member 3** | Data Engineering & Scraping Lead | `crawler/`, `data/raw/`, `data/processed/` | Multi-source travel spiders (NativeIndonesia, IndonesiaTravel, Wisato) targeting 600–800 articles, duplicate checking pipeline (>95% text similarity), deduplication reports |
| **Member 4** | IR Evaluation, QA, & Academic Report Lead | `data/ground_truth/`, `docs/report/` | Ground-truth test queries, manual binary relevance judgments (`qrels.csv`), automated evaluator (P@10, Recall, F1, MAP), experimental analysis, academic report Bab I–V |

---

## Architecture Overview

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

- **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons, Recharts. Features single-model and Side-by-Side Split View (BM25 vs LM Dirichlet vs Baseline), keyword snippet highlighting, interactive Rocchio feedback buttons, and an evaluation metrics dashboard.
- **Backend API**: Python 3.11, FastAPI, Uvicorn, PySastrawi stemmer, `elasticsearch-py`. Exposes REST endpoints for search, relevance feedback, query expansion, and posting list inspection.
- **Search & Indexing Engine**: Elasticsearch 8.13.x (Apache Lucene).
  - `wisata_custom`: Indexes preprocessed tokens using `WhitespaceAnalyzer` with `custom_bm25` ($k_1=1.2, b=0.75$) and `custom_lm_dirichlet` ($\mu=2000$) similarities, and term vectors enabled.
  - `wisata_baseline`: Indexes raw text using default `StandardAnalyzer` and default BM25 as an experimental control group.
- **Query Expansion**: Curated Indonesian tourism synonym dictionary ($\ge 15$ bidirectional pairs) expanding destination terms (e.g. `curug` $\leftrightarrow$ `air terjun`, `pelesir` $\leftrightarrow$ `wisata`).
- **Relevance Feedback**: Classic **Rocchio Algorithm** ($\alpha=1.0, \beta=0.75, \gamma=0.15$) dynamically recalculating query term weights using Lucene document term vectors.

---

## Quickstart

### 1. Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Node.js 18+ (for frontend development)

### 2. Start Elasticsearch Service
```bash
docker compose up -d elasticsearch
```
Verify Elasticsearch is running:
```bash
curl -s http://localhost:9200/_cluster/health
```

### 3. Backend Setup & Ingestion
```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed and index initial corpus into Elasticsearch
python3 -m backend.app.engine.seed

# 4. Start FastAPI backend server
uvicorn backend.app.main:app --reload --port 8000
```

- **Interactive API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## Automated Tests & Quality Verification

Run the complete test suite (33 unit tests):
```bash
pytest tests/ -v
# or
make test
```

Run the 7-Gate Quality Pipeline Verification:
```bash
python3 scripts/verify_pipeline.py
# or
make verify
```

The pre-flight gatekeeper enforces:
1. Directory and scaffolding integrity
2. Dependency declarations in `requirements.txt`
3. Makefile automation targets
4. Clean Text Policy (zero decorative icons/emojis)
5. No Artificial Timelines Rule
6. AGENTS.md protocol compliance
7. Core retrieval and evaluation sanity checks

---

## Sample Queries and Demonstration

| Query | Category | Model 1 (BM25) Top Result | Model 2 (LM Dirichlet) Top Result |
| :--- | :--- | :--- | :--- |
| `curug bogor alami` | Wisata Alam (Air Terjun) | Pesona Keindahan Curug Leuwi Hejo Bogor | Sensasi Sejuk Tujuh Tingkat Air Terjun Curug Cilember Bogor |
| `pantai pasir putih bali` | Wisata Bahari (Pantai) | Eksotisme Pasir Putih Pantai Kuta Bali | Romantisme Senja dan Mistisisme Pantai Parangtritis Jogja |
| `candi peninggalan mataram kuno` | Wisata Budaya (Candi) | Kemegahan Candi Borobudur Warisan Mataram Kuno di Magelang | Situs Sejarah Candi Gedong Songo di Lereng Gunung Ungaran |
| `snorkeling terumbu karang` | Wisata Bahari (Diving) | Surga Bawah Laut dan Snorkeling di Kepulauan Raja Ampat | Berenang Bersama Ubur-ubur Tanpa Sengat di Pulau Kakaban Derawan |
| `kawah belerang danau toska` | Wisata Alam (Gunung) | Pesona Api Biru dan Danau Kawah Ijen Banyuwangi | Pesona Kawah Ratu dan Gunung Tangkuban Parahu Bandung |

---

## Repository Structure

```
mesin-pencari-wisata-nusantara/
├── backend/
│   ├── app/
│   │   ├── engine/
│   │   │   ├── preprocessor.py       # PySastrawi + domain cleaning
│   │   │   ├── indexer.py            # Dual-index manager & posting lists
│   │   │   ├── searcher.py           # BM25, LM Dirichlet, & Baseline execution
│   │   │   ├── query_expansion.py    # 45-entry synonym dictionary
│   │   │   ├── rocchio.py            # Relevance feedback with term vectors
│   │   │   └── seed.py               # Local corpus ingestion runner
│   │   ├── api/
│   │   │   ├── routes.py             # FastAPI REST endpoints
│   │   │   └── schemas.py            # Pydantic data schemas
│   │   └── main.py                   # Application entrypoint & CORS
│   └── Dockerfile
├── crawler/                          # Multi-source web spiders (Member 3)
├── data/
│   ├── raw/                          # Crawled raw corpus (Member 3)
│   ├── processed/                    # Clean deduplicated corpus
│   └── ground_truth/                 # Test queries and qrels (Member 4)
├── docs/
│   ├── evidence/                     # Screenshots, logs, deduplication reports
│   ├── report/                       # Academic report Bab I–V (Member 4)
│   ├── slides/                       # Presentation slide deck (Member 1)
│   ├── TEAM_WORKFLOW.md              # Living team governance
│   └── PROGRESS.md                   # 10-component progress tracker
├── frontend/                         # React 18 + Vite web UI (Member 1)
├── scripts/
│   └── verify_pipeline.py            # 7-Gate pre-flight quality gatekeeper
├── tests/                            # Automated pytest suite (33 tests)
├── .github/
│   ├── workflows/ci.yml              # GitHub Actions CI workflow
│   └── pull_request_template.md      # PR submission template
├── docker-compose.yml                # Full stack container orchestration
├── Makefile                          # Unified project commands
├── requirements.txt                  # Python dependencies
└── README.md                         # Project documentation
```

---

## License & Academic Disclaimer

Developed for academic evaluation purposes in the **Praktikum Penelusuran Informasi 2025/2026** course at **FMIPA Universitas Syiah Kuala**. All crawled article content belongs to their respective original publication sources.
