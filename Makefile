.PHONY: help install dev up down logs clean migrate test lint format

help:
	@echo "Harezmi Intelligence - Development Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install       - Install all dependencies"
	@echo ""
	@echo "Docker Management:"
	@echo "  make up            - Start Docker services (postgres, redis)"
	@echo "  make down          - Stop Docker services"
	@echo "  make logs          - View Docker service logs"
	@echo ""
	@echo "Development:"
	@echo "  make dev           - Start API server in development mode"
	@echo "  make migrate       - Run database migrations"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          - Run linter (ruff)"
	@echo "  make format        - Format code (black)"
	@echo "  make test          - Run tests with coverage"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         - Remove cache files and virtual env"

install:
	@echo "Installing dependencies with UV..."
	uv sync --all-groups

dev:
	@echo "Starting FastAPI development server..."
	uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

up:
	@echo "Starting Docker services..."
	docker compose -f infra/docker-compose.dev.yml up -d
	@echo "✅ Services running (postgres on 5432, redis on 6379)"

down:
	@echo "Stopping Docker services..."
	docker compose -f infra/docker-compose.dev.yml down

logs:
	@echo "Viewing Docker logs..."
	docker compose -f infra/docker-compose.dev.yml logs -f

migrate:
	@echo "Running database migrations..."
	alembic upgrade head

migrate-create:
	@read -p "Enter migration name: " NAME; \
	alembic revision --autogenerate -m "$$NAME"

test:
	@echo "Running tests with coverage..."
	pytest tests/ -v --cov=apps --cov=core --cov=services --cov-report=html

lint:
	@echo "Running linter (ruff)..."
	ruff check . --fix

format:
	@echo "Formatting code with black..."
	black . --line-length 100

format-check:
	@echo "Checking code format..."
	black . --check --line-length 100
	ruff check .

clean:
	@echo "Cleaning up..."
	rm -rf .pytest_cache htmlcov .coverage build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✅ Cleanup complete"

mypy:
	@echo "Running type checking..."
	mypy apps core services --ignore-missing-imports

pre-commit:
	@echo "Running pre-commit hooks..."
	pre-commit run --all-files
