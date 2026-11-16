---
name: wisata-search-workflow
description: End-to-end guidance for the Indonesian Tourism Vertical Search Engine (multi-source crawling, dual-index Elasticsearch, Okapi BM25 vs LM Dirichlet, Sastrawi preprocessing, Rocchio relevance feedback, React split-view UI, and pre-flight quality verification).
---

# Wisata Search Workflow — Team & Agent Guide

This skill directs AI agents and team members working on the **Indonesian Tourism Vertical Search Engine** (`mesin-pencari-wisata-nusantara`) for Kelompok 10 in the Praktikum Penelusuran Informasi (Information Retrieval Lab) course at FMIPA Universitas Syiah Kuala.

---

## Trigger Keywords

`wisata nusantara`, `travel search`, `mesin pencari wisata`, `crawling`, `nativeindonesia`, `indonesiatravel`, `wisato`, `bm25`, `lm dirichlet`, `sastrawi`, `rocchio`, `evaluator`, `qrels`, `map`, `precision`, `verify pipeline`

---

## 1. Team Role Allocation & Workspaces (4 Members)

Before starting any task, determine which member is being assisted:

| Member | Primary Role | Designated Workspace | Dedicated Git Branch | Key Deliverables |
| :--- | :--- | :--- | :--- | :--- |
| **Member 1** | Frontend & UI Lead | `frontend/`<br>`docs/slides/` | `feature/frontend-ui` | React 18, Vite, Tailwind CSS, Side-by-Side Split View (BM25 vs LM Dirichlet vs Baseline), snippet highlighting, Rocchio feedback buttons, Recharts dashboard, slide presentasi |
| **Member 2** | Core IR & Backend Lead | `backend/`<br>`docker-compose.yml` | `feature/core-ir-engine` | Custom travel preprocessing (PySastrawi), dual-index Elasticsearch mappings, BM25 & LM Dirichlet retrieval, posting-list inspector, query expansion, Rocchio engine, FastAPI, Docker |
| **Member 3** | Data Engineering & Scraping Lead | `crawler/`<br>`data/raw/`<br>`data/processed/`<br>`docs/evidence/` | `feature/crawler-data` | Multi-source travel spiders (NativeIndonesia, IndonesiaTravel, Wisato) targeting 600–800 docs, deduplication pipeline (>95% text similarity), raw & clean corpora, duplicate verification report |
| **Member 4** | IR Evaluation, QA, & Academic Report Lead | `data/ground_truth/`<br>`docs/report/` | `feature/evaluation-report` | 10–15 test queries, manual binary relevance judgments (`qrels.csv`), automated evaluator (P@10, Recall, F1, MAP), experimental comparative analysis, academic report Bab I–V |

---

## 2. Parallel vs Sequential Dependency Rules

To prevent workflow bottlenecks:

### Tasks that can be worked on IMMEDIATELY in PARALLEL:
- **Member 1**: Wireframe and style React components using mock API data in `frontend/`. Design presentation slide deck in `docs/slides/`.
- **Member 2**: Maintain and optimize core IR engine (BM25, LM Dirichlet, Rocchio, FastAPI endpoints).
- **Member 3**: Implement web scraping spiders in `crawler/spiders/` and build duplicate checking script.
- **Member 4**: Formulate test queries and draft Bab I (Pendahuluan) & Bab II (Tinjauan Pustaka) of the academic report.

### Tasks that have SEQUENTIAL DEPENDENCIES:
1. **Full Production Ingestion**: Member 2 runs indexing on full dataset **after** Member 3 delivers deduplicated $\ge 500$ documents to `data/processed/corpus_clean.json`.
2. **Frontend Live Integration**: Member 1 connects `frontend/src/services/api.js` to live search **after** Member 2's FastAPI endpoints are verified.
3. **Full Benchmark Reporting**: Member 4 executes evaluation benchmarks **after** Member 2's indexing is complete and Member 3's corpus is in place.
4. **Final Demo & Video**: All members record live demo walkthroughs **after** Docker Compose runs cleanly end-to-end.

Consult `docs/PROGRESS.md` for live milestone status!

---

## 3. Workflow Steps for Agents

### Step 1: Pre-Flight Context Check
1. Read `docs/PROGRESS.md` to identify pending vs completed milestones.
2. Confirm active git branch matches the assigned member's workspace (never commit directly to `main`).
3. Run `make test` and `make verify` before making changes to ensure green baseline.

### Step 2: Implementation & TDD
- Always follow Test-Driven Development (TDD): write unit tests in `tests/`, watch them fail, implement minimal code, verify green.
- Respect Clean Text Policy: ZERO decorative pictographic emojis or icons in code or markdown.
- Respect No Artificial Timelines Rule: Never mention artificial timelines, deadlines, or duration estimates.

### Step 3: Pre-PR Quality Verification (Mandatory Gate)
Before opening a Pull Request, run:
```bash
python3 scripts/verify_pipeline.py
# or
make verify
```
All 7 quality gates must report `[PASS]`.

### Step 4: Update Progress Checklist
Open `docs/PROGRESS.md`, check off completed items (`- [x]`), and update component status.

### Step 5: Pull Request & Issue Linking
Commit changes using Conventional Commits (`feat(`, `fix(`, `docs(`, `chore(`) and open a PR targeting `main`.
Link the PR to the relevant issue using standard keywords (e.g. `Closes #1`, `Closes #2`).

---

## 4. Issue Creation Protocol

1. Create issue using `ghx issue create`:
   ```bash
   ghx issue create \
     --title "[<Category>] <Clear Title>" \
     --body "### Penanggung Jawab: ...\n**Branch**: ...\n#### Deskripsi Tugas:\n- [ ] ...\n#### Kriteria Sukses:\n- Lulus 'make verify'"
   ```
   Valid categories: `[Frontend]`, `[Core IR]`, `[Data]`, `[Report]`, `[Demo]`, `[Bugfix]`.
2. Register the issue in `docs/PROGRESS.md`.
3. Provide an explanatory comment whenever closing or modifying an issue's status.
