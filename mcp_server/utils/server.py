from fastmcp import FastMCP

mcp = FastMCP("weather")

http_app = mcp.http_app(path="/mcp")