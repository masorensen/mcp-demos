# Simplified MCP test client that bypasses SSE complexity
from typing import List, Dict, Any


class SimpleMCPTestClient:
    """Simplified test client for MCP endpoints that avoids SSE complexity."""
    
    def __init__(self, test_client):
        self.client = test_client
        self.session_id = None
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools using direct MCP instance access."""
        from mcp_server.utils.server import mcp
        tools = await mcp.get_tools()
        return [
            {
                "name": name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for name, tool in tools.items()
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call an MCP tool directly without going through SSE."""
        from mcp_server.utils.server import mcp
        tools = await mcp.get_tools()
        
        if tool_name not in tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        # Call the tool function directly
        tool_func = tools[tool_name].function
        return await tool_func(**arguments)
    
    def test_endpoint_requires_sse(self, path: str = "/mcp") -> bool:
        """Test that an endpoint requires SSE headers."""
        response = self.client.get(path)
        return response.status_code == 406
    
    def test_endpoint_with_sse_header(self, path: str = "/mcp") -> int:
        """Test endpoint with SSE header returns expected status."""
        response = self.client.get(path, headers={"Accept": "text/event-stream"})
        return response.status_code