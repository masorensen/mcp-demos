build:
	uv sync
run:
	docker compose up -d
	uv run python -m mcp_server.main