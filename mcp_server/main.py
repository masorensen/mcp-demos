from fastapi import FastAPI
from mcp_server.tools.weather import get_weather
from langchain_mcp_adapters import MCPServer

app = FastAPI()
mcp_server = MCPServer(app)

# Register the weather tool
mcp_server.register_tool(get_weather)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)