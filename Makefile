# ============================================================
#  TruthLens AI — Makefile
#  Common development commands
# ============================================================

.PHONY: help install install-nlp dev api collector migrate test lint format

help:
	@echo ""
	@echo "TruthLens AI — Available Commands"
	@echo "=================================="
	@echo "  make install      Install backend dependencies"
	@echo "  make install-nlp  Install NLP worker dependencies (heavy)"
	@echo "  make api          Start FastAPI development server"
	@echo "  make collector    Run RSS collector once"
	@echo "  make nlp          Run NLP worker to process raw articles"
	@echo "  make migrate      Run Alembic database migrations"
	@echo "  make migrate-new  Create a new migration (NAME=your_name)"
	@echo "  make test         Run all tests"
	@echo "  make test-unit    Run unit tests only"
	@echo "  make lint         Run ruff linter"
	@echo "  make format       Format code with black + ruff"
	@echo "  make clean        Remove cache files"
	@echo ""

# --- Installation ---
install:
	pip install -r requirements.txt

install-nlp:
	pip install -r requirements-nlp.txt
	python -m spacy download en_core_web_sm

# --- Development ---
api:
	uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

collector:
	python services/collector/rss_collector.py

collector-guardian:
	python services/collector/guardian_collector.py

nlp:
	python services/nlp/nlp_worker.py

# --- Database ---
migrate:
	alembic upgrade head

migrate-new:
	alembic revision --autogenerate -m "$(NAME)"

migrate-down:
	alembic downgrade -1

migrate-history:
	alembic history --verbose

# --- Testing ---
test:
	pytest tests/ -v --tb=short

test-unit:
	pytest tests/unit/ -v

test-api:
	pytest tests/api/ -v --base-url=http://localhost:8000

test-cover:
	pytest tests/ --cov=. --cov-report=html

# --- Code Quality ---
lint:
	ruff check .

lint-fix:
	ruff check . --fix

format:
	black .
	ruff check . --fix

typecheck:
	mypy apps/ shared/ services/ --ignore-missing-imports

# --- Cleanup ---
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
