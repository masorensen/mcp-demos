build:
	uv sync
	uv sync --extra test

run:
	docker compose up -d
	uv run python -m mcp_server.main

test:
	uv run pytest --cov=mcp_server --cov-report=term-missing --cov-report=xml

test-unit:
	uv run pytest -m "not integration"

test-integration:
	uv run pytest -m integration

test-coverage:
	uv run pytest --cov=mcp_server --cov-report=term-missing --cov-report=xml

test-coverage-html:
	uv run pytest --cov=mcp_server --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

test-verbose:
	uv run pytest -vvs

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "coverage.xml" -delete 2>/dev/null || true
	rm -rf htmlcov/ 2>/dev/null || true
	@echo "Cache and test artifacts cleaned"