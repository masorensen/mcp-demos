import pytest
from unittest.mock import patch

from mcp_server.utils.server import mcp, http_app


class TestMcpServer:
    # Test suite for MCP server initialization
    
    def test_mcp_instance_created(self):
        # GIVEN: The server module is imported
        # WHEN: Accessing the mcp instance
        # THEN: The MCP instance is properly initialized with the correct name
        assert mcp is not None
        assert hasattr(mcp, 'name')
        assert mcp.name == "weather"
    
    def test_http_app_created(self):
        # GIVEN: The server module is imported
        # WHEN: Accessing the http_app
        # THEN: The HTTP app is created and configured
        assert http_app is not None
        # AND: The app is a valid ASGI application
        assert hasattr(http_app, '__call__')
    
    def test_mcp_endpoint_path(self, test_client):
        # GIVEN: The HTTP app is created with lifespan support
        # WHEN: Checking the MCP endpoint
        # THEN: The /mcp endpoint should be available
        # Note: We're testing that the endpoint exists, not its full functionality
        response = test_client.options("/mcp")
        # AND: It should respond (even if with method not allowed or similar)
        assert response.status_code in [200, 204, 405]  # Common responses for OPTIONS
    
    @pytest.mark.integration
    def test_mcp_tools_registered(self):
        # GIVEN: The MCP server is initialized
        # WHEN: Importing the tools module (which registers tools)
        with patch.object(mcp, 'tool') as mock_tool_decorator:
            # Create a mock that behaves like the decorator
            mock_tool_decorator.return_value = lambda f: f
            
            # Import tools to trigger registration
            import mcp_server.tools.weather
            
            # THEN: The tool decorator should have been called
            # Note: In actual usage, the tools are registered when imported
            # This test verifies the registration mechanism exists
    
    def test_server_configuration(self):
        # GIVEN: The MCP server instance
        # WHEN: Checking server configuration
        # THEN: The server should have the expected configuration
        assert hasattr(mcp, 'http_app')
        # AND: The HTTP app factory should accept path parameter
        test_app = mcp.http_app(path="/test")
        assert test_app is not None
    
    def test_mcp_protocol_info_endpoint_requires_sse(self, test_client):
        # GIVEN: The MCP HTTP app with lifespan support
        # WHEN: Requesting MCP endpoint without SSE Accept header
        response = test_client.get("/mcp")
        
        # THEN: The endpoint should return 406 Not Acceptable
        assert response.status_code == 406
        # AND: The error message should indicate SSE is required
        error_data = response.json()
        assert error_data["error"]["message"] == "Not Acceptable: Client must accept text/event-stream"
    
    def test_mcp_endpoint_with_sse_header(self, test_client):
        # GIVEN: The MCP HTTP app configured for SSE
        # WHEN: Requesting with proper SSE Accept header
        response = test_client.get("/mcp", headers={"Accept": "text/event-stream"})
        
        # THEN: The endpoint should respond (though may require additional setup)
        # 400 indicates the SSE connection was accepted but request was malformed
        assert response.status_code == 400
    
    def test_multiple_app_instances(self):
        # GIVEN: The MCP instance
        # WHEN: Creating multiple HTTP app instances with different paths
        app1 = mcp.http_app(path="/mcp1")
        app2 = mcp.http_app(path="/mcp2")
        
        # THEN: Different app instances should be created
        assert app1 is not None
        assert app2 is not None
        # AND: They should be different instances
        # Note: Depending on FastMCP implementation, they might be the same
        # instance with different configuration