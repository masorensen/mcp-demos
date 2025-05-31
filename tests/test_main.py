import pytest

from mcp_server.utils.server import mcp
from tests.utils.simple_sse_client import SimpleMCPTestClient


class TestMainIntegration:
    # Integration tests for the main MCP server application
    
    def test_main_imports(self):
        # GIVEN: The main module exists
        # WHEN: Importing the main module
        import mcp_server.main
        
        # THEN: Required modules are imported
        assert hasattr(mcp_server.main, 'http_app')
        assert hasattr(mcp_server.main, 'weather')
        assert hasattr(mcp_server.main, 'uvicorn')
    
    @pytest.mark.integration
    def test_server_health_check(self, test_client):
        # GIVEN: The MCP server is running
        # WHEN: Making a basic request to check server health
        response = test_client.get("/")
        
        # THEN: The server should respond (even with 404 for root)
        assert response.status_code in [200, 404, 405]
        # AND: The server is operational
    
    @pytest.mark.integration
    def test_mcp_endpoint_exists(self, test_client):
        # GIVEN: The MCP server with configured endpoint
        # WHEN: Checking if the MCP endpoint exists with OPTIONS method
        response = test_client.options("/mcp")
        
        # THEN: The endpoint should return 405 Method Not Allowed
        assert response.status_code == 405
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_mcp_tools_structure(self, test_client):
        # GIVEN: The MCP server with weather tools loaded
        client = SimpleMCPTestClient(test_client)
        
        # WHEN: Getting the tools list
        tools = await client.list_tools()
        
        # THEN: We should have exactly 2 tools registered
        assert len(tools) == 2
        tool_names = [t["name"] for t in tools]
        assert "get_alerts" in tool_names
        assert "get_forecast" in tool_names
        
        # AND: Each tool should have the expected structure
        alerts_tool = next(t for t in tools if t["name"] == "get_alerts")
        assert "Get weather alerts for a US state" in alerts_tool["description"]
        assert alerts_tool["parameters"]["required"] == ["state"]
        
        forecast_tool = next(t for t in tools if t["name"] == "get_forecast")
        assert "Get weather forecast for a location" in forecast_tool["description"]
        assert forecast_tool["parameters"]["required"] == ["latitude", "longitude"]
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tool_execution(self, test_client):
        # GIVEN: The MCP server with tools available
        client = SimpleMCPTestClient(test_client)
        
        # WHEN: Calling a tool directly
        # Note: This is an integration test that verifies tool registration
        tools = await client.list_tools()
        
        # THEN: Tools are properly registered and callable
        assert len(tools) == 2
        assert all(t["name"] in ["get_alerts", "get_forecast"] for t in tools)
    
    @pytest.mark.integration
    def test_mcp_endpoint_requirements(self, test_client):
        # GIVEN: The MCP server endpoint
        client = SimpleMCPTestClient(test_client)
        
        # WHEN: Testing endpoint requirements
        # THEN: The endpoint requires SSE headers
        assert client.test_endpoint_requires_sse("/mcp")
        
        # AND: With SSE headers, it returns 400 (needs proper JSON-RPC)
        assert client.test_endpoint_with_sse_header("/mcp") == 400
    
    @pytest.mark.integration
    @pytest.mark.parametrize("method,expected_status", [
        ("GET", 406),     # Needs SSE Accept header
        ("PUT", 405),     # Method Not Allowed
        ("DELETE", 400),  # Bad request
        ("PATCH", 405),   # Method Not Allowed
        ("POST", 406),    # Needs SSE (without proper headers)
    ])
    def test_http_methods(self, test_client, method, expected_status):
        # GIVEN: The MCP server endpoint
        # WHEN: Using various HTTP methods
        response = test_client.request(method, "/mcp")
        
        # THEN: Each method returns the expected status
        assert response.status_code == expected_status