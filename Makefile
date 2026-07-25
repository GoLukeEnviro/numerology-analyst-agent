.PHONY: help install sync lint format typecheck test test-cov all clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

sync: ## Install all dependency groups into .venv (uv)
	uv sync --all-groups

install: sync ## Alias for sync

format: ## Format code with ruff
	uv run ruff format .

lint: ## Lint with ruff (format check + check)
	uv run ruff format --check .
	uv run ruff check .

typecheck: ## Strict mypy on src, apps, tests
	uv run mypy src apps tests

test: ## Run the full test suite
	uv run pytest

test-cov: ## Run tests with coverage, fail under 85%
	uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=85

all: lint typecheck test-cov ## Run all Quality Gates (Master Contract §11)

clean: ## Remove build/test caches
	rm -rf .mypy_cache .ruff_cache .pytest_cache .coverage coverage.xml htmlcov build dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
