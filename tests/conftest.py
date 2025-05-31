import pytest
from fastapi.testclient import TestClient

from mcp_server.utils.server import mcp
from tests.helpers import weather_test_data  # Importing this function in conftest makes it a fixture


@pytest.fixture
def test_client():
    # Import tools to ensure they're registered
    import mcp_server.tools.weather
    
    # Create a new app instance
    test_app = mcp.http_app(path="/mcp")
    with TestClient(test_app) as client:
        yield client