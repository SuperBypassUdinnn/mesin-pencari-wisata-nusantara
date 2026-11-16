# Agent Protocol — mesin-pencari-wisata-nusantara (Kelompok 10)

## 1. Mandatory Session Start Protocol

At the start of every session, before reading or writing code:

1. Read the task brief for the assigned task (`.superpowers/sdd/2026-11-16-wisata-search-engine-implementation/task-<N>-brief.md`).
2. Read `docs/TEAM_WORKFLOW.md` to confirm directory ownership and branch conventions.
3. Read `docs/PROGRESS.md` to confirm which components are in scope and their checkbox status.
4. Confirm the active branch matches the assigned task owner (e.g., Task 1–9 backend work runs on `feature/core-ir-engine`).
5. Run `make test` and `make verify` to confirm the baseline is green before making changes.

## 2. Directory Boundary Enforcement

| Directory | Owner | Rule |
| :--- | :--- | :--- |
| `frontend/`, `docs/slides/` | Member 1 | Other members must not touch without review and approval |
| `backend/`, `docker-compose.yml` | Member 2 | Other members must not touch without review and approval |
| `crawler/`, `data/raw/`, `data/processed/`, `docs/evidence/` | Member 3 | Other members must not touch without review and approval |
| `data/ground_truth/`, `docs/report/` | Member 4 | Other members must not touch without review and approval |
| Root config (`.gitignore`, `requirements.txt`, `Makefile`, `AGENTS.md`, `scripts/`) | Shared | Team consensus required before changes |

## 3. Clean Text Policy

Zero decorative pictographic emojis or icons in any file: code, comments, documents, commit messages, PR descriptions, or session artifacts. Use standard markdown headers and clean bullet points only.

## 4. No Artificial Timelines Rule

Never mention artificial timelines, deadlines, or duration estimates (for example `N minggu`, `N hari`) in documents or code comments.

## 5. Language

Formal technical English for all engineering documents, code comments, commit messages, and workflows. Group identification: Kelompok 10.

## 6. Pre-commit Checks

Before any commit:

1. `make test` passes (`pytest tests/ -v`).
2. `make verify` passes (`python3 scripts/verify_pipeline.py`, all 7 gates).
3. Clean Text Policy verified (no emojis or decorative icons).
4. No artificial timelines mentioned in changed documents or code.
5. Changes confined to owned directories unless team consensus obtained for shared files.

## 7. Quality Gate Script

Run locally before every push:

```bash
python3 scripts/verify_pipeline.py
# or
make verify
```
