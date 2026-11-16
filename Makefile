.PHONY: run test verify lint help

run:
	@echo "Starting backend development server on port 8000..."
	python3 -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

verify:
	python3 scripts/verify_pipeline.py

lint:
	@echo "Lint checks not yet configured; run 'make test' and 'make verify'."

help:
	@echo "Available targets:"
	@echo "  make run    - start the FastAPI backend development server"
	@echo "  make test   - run the pytest suite"
	@echo "  make verify - run the automated 7-gate quality pipeline"
	@echo "  make lint   - run static lint checks (placeholder)"
