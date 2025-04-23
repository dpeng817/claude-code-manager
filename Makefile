.PHONY: help ruff ruff-format ruff-check ruff-fix install dev clean

help:
	@echo "Available commands:"
	@echo "  make help        - Show this help message"
	@echo "  make ruff        - Run both ruff format and ruff check"
	@echo "  make ruff-format - Run ruff formatter only"
	@echo "  make ruff-check  - Run ruff linter only"
	@echo "  make ruff-fix    - Run ruff with autofix to correct issues"
	@echo "  make install     - Install the package"
	@echo "  make dev         - Install the package in development mode with dev dependencies"
	@echo "  make clean       - Remove build artifacts and cache directories"

ruff: ruff-format ruff-check

ruff-format:
	ruff format .

ruff-check:
	ruff check .

ruff-fix:
	ruff check --fix .

install:
	uv pip install -e .

dev:
	uv pip install -e ".[dev]"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete 