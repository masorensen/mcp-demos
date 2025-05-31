from mcp_server.utils.server import http_app
import uvicorn
from mcp_server.tools import weather

if __name__ == "__main__":
    uvicorn.run(http_app, host="127.0.0.1", port=8000) # pragma: no cover