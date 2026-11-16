# Project Progress Tracker — Kelompok 10

Living checklist tracking all 10 UAS evaluation components. Updated by all team members during team meetings. `- [ ]` = not started, `- [x]` = complete.

## 1. Korpus & Crawling (10%)
- [ ] Crawl 600–800 Indonesian tourism articles from NativeIndonesia.com, Indonesia.travel, Wisato.id
- [ ] Deduplicate corpus (>95% similarity threshold), retain >= 500 unique documents
- [ ] Produce `data/raw/corpus_raw.json` and `data/raw/corpus_raw.csv`
- [ ] Produce `data/processed/corpus_clean.json` and `data/processed/corpus_clean.csv`
- [ ] Publish `docs/evidence/duplicate_report.md`

## 2. Custom Preprocessing (15%)
- [ ] Implement HTML, emoji, ticket price, and operational hours cleaning
- [ ] Implement domain stopword removal with tourism whitelist
- [ ] Implement PySastrawi Indonesian morphological stemming
- [ ] Integrate with Elasticsearch WhitespaceAnalyzer
- [ ] Provide side-by-side preprocessing inspection utility

## 3. Indexing & Dual Retrieval Models (20%)
- [ ] Create `wisata_custom` index with custom preprocessing fields
- [ ] Create `wisata_baseline` index with StandardAnalyzer
- [ ] Implement Okapi BM25 (k1=1.2, b=0.75)
- [ ] Implement LM Dirichlet (mu=2000)
- [ ] Implement posting list introspection (tf, df, document pointers)

## 4. Query Expansion & Rocchio Feedback (10%)
- [ ] Curate Indonesian tourism synonym dictionary (>= 15 pairs)
- [ ] Verify expansion on >= 5 sample queries
- [ ] Implement Rocchio algorithm (alpha=1.0, beta=0.75, gamma=0.15)
- [ ] Integrate Elasticsearch _termvectors for relevance feedback

## 5. System Evaluation (15%)
- [ ] Define >= 10 test queries spanning tourism categories
- [ ] Annotate manual binary relevance judgments (qrels.csv)
- [ ] Implement automated evaluator (Precision@10, Recall, F1, MAP)
- [ ] Produce comparison table across all 3 model configurations

## 6. Search User Interface (10%)
- [ ] Build React 18 + Vite + Tailwind CSS search page
- [ ] Implement side-by-side model split view
- [ ] Implement keyword snippet highlighting and source portal badges
- [ ] Implement interactive relevance feedback buttons per result
- [ ] Build Recharts evaluation metrics dashboard

## 7. Presentation & Q&A (20%)
- [ ] Create presentation slide deck (`docs/slides/`)
- [ ] Prepare live demo walkthrough script
- [ ] Document `README.md` with installation and demo instructions
- [ ] Deliver team presentation and answer evaluation questions

## 8. Repository Governance (Task 1)
- [x] `.gitignore` created
- [x] `requirements.txt` created
- [x] `Makefile` created
- [x] `docs/TEAM_WORKFLOW.md` created
- [x] `docs/PROGRESS.md` created
- [x] `AGENTS.md` created
- [x] `scripts/verify_pipeline.py` created
- [x] `tests/test_scaffolding.py` created and passing

## 9. Docker Portability
- [ ] Create `docker-compose.yml` (Elasticsearch, FastAPI backend, React frontend)
- [ ] Create `backend/Dockerfile`
- [ ] Create `frontend/Dockerfile`
- [ ] Verify `docker compose up --build` single-command startup

## 10. Academic Deliverables
- [ ] Write academic report Bab I–V (`docs/report/`)
- [ ] Organize evidence artifacts (`docs/evidence/`)
- [ ] Archive evaluation benchmark tables and results
