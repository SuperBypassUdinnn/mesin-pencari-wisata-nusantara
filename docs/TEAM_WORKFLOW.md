# Team Collaboration Workflow — Kelompok 10

## 1. Team Members and Directory Ownership

| Member | Role | Directory Ownership | Primary Deliverables |
| :--- | :--- | :--- | :--- |
| Member 1 | Frontend & UI Lead | `frontend/` | React search UI, split-view comparison, relevance feedback controls, Recharts dashboard, inspector modals, presentation slide design |
| Member 2 | Core IR Engine & Backend Lead | `backend/`, `docker-compose.yml` | Indonesian preprocessing pipeline, dual-index Elasticsearch setup, BM25 and LM Dirichlet retrieval models, posting-list inspector, query expansion, Rocchio feedback engine, FastAPI REST endpoints |
| Member 3 | Data Engineering, Evaluation & Report Lead | `crawler/`, `data/`, `docs/report/`, `docs/evidence/` | Multi-source crawler spiders, deduplication pipeline, ground-truth queries and qrels, automated evaluator, academic report Bab I–V, evidence documentation |

No member shall modify files inside another member's owned directory without prior review and explicit approval. Root configuration files (`.gitignore`, `requirements.txt`, `Makefile`, `AGENTS.md`, `scripts/`) are shared and require team consensus before changes.

## 2. Branch Conventions

All work is branched from `main`. Protected branches: `main`.

| Branch Name | Purpose | Owner |
| :--- | :--- | :--- |
| `main` | Production-ready mainline; receives fast-forward merges only | All (merge gate) |
| `feature/core-ir-engine` | Preprocessing, indexing, retrieval, query expansion, Rocchio, API | Member 2 |
| `feature/frontend-ui` | React UI, split view, feedback controls, dashboard | Member 1 |
| `feature/crawler-data` | Crawler spiders, deduplication, ground truth, evaluation data | Member 3 |
| `docs/academic-report` | Academic report Bab I–V and supporting evidence | Member 3 |

Naming rule: `feature/<area>` for feature work, `docs/<area>` for documentation-only work. Branch from `main`, rebase onto `main` before merging, and merge with `--ff-only`.

## 3. Pull Request Protocol

1. Create a feature branch from `main` following the naming convention above.
2. Implement changes strictly within your owned directory (or shared root files with team consent).
3. Run the local quality gate before pushing: `make test` and `make verify` (or `python3 scripts/verify_pipeline.py`).
4. Open a Pull Request against `main` from the feature branch.
5. Require at least one approval from another team member before merge.
6. Squash and merge with `--ff-only`; delete the feature branch after merge.
7. PR description must state: problem context, component changes, verification results (tests pass, verify gate passes), and any test artifacts.

## 4. Local Development Cycle

```bash
# 1. Clone and enter the repository
# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate
# 3. Install dependencies
pip install -r requirements.txt
# 4. Run the test suite
make test
# 5. Run the quality gate
make verify
# 6. Start the backend (when available)
make run
```

## 5. Quality Gates

- `pytest tests/ -v` must pass for all committed test suites.
- `python3 scripts/verify_pipeline.py` must pass all 7 gates before any PR is merged.
- Clean Text Policy: zero decorative emojis or icons in code, comments, or documents.
- No artificial timelines, deadlines, or duration estimates in any document or code comment.

## 6. Issue and Commit Labels

Use conventional commit prefixes: `feat(`, `fix(`, `docs(`, `chore(`, `test(`, `refactor(`. Prefix commit subjects with the responsible area, e.g. `chore(scaffold): initialize repository governance`.
