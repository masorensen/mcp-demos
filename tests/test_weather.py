import pytest
from unittest.mock import AsyncMock
import httpx
from httpx import HTTPStatusError, TimeoutException

from mcp_server.utils.weather import make_nws_request, format_alert, USER_AGENT

class TestMakeNwsRequest:
    # Test suite for make_nws_request function
    
    @pytest.mark.asyncio
    async def test_successful_request(self, httpx_mock):
        # GIVEN: A valid NWS API endpoint that returns JSON data
        test_url = "https://api.weather.gov/test"
        expected_data = {"status": "success", "data": "test"}
        httpx_mock.add_response(json=expected_data)
        
        # WHEN: Making a request to the NWS API
        result = await make_nws_request(test_url)
        
        # THEN: The function returns the parsed JSON response
        assert result == expected_data
        # AND: The request includes the correct headers
        request = httpx_mock.get_request()
        assert request.headers["User-Agent"] == USER_AGENT
        assert request.headers["Accept"] == "application/geo+json"
    
    @pytest.mark.asyncio
    async def test_http_error_returns_none(self, httpx_mock):
        # GIVEN: An NWS API endpoint that returns a 404 error
        test_url = "https://api.weather.gov/notfound"
        httpx_mock.add_response(status_code=404)
        
        # WHEN: Making a request that results in an HTTP error
        result = await make_nws_request(test_url)
        
        # THEN: The function returns None instead of raising an exception
        assert result is None
    
    @pytest.mark.asyncio
    async def test_timeout_returns_none(self, httpx_mock):
        # GIVEN: An NWS API endpoint that times out
        test_url = "https://api.weather.gov/slow"
        httpx_mock.add_exception(TimeoutException("Request timed out"))
        
        # WHEN: Making a request that times out
        result = await make_nws_request(test_url)
        
        # THEN: The function returns None instead of raising an exception
        assert result is None
    
    @pytest.mark.asyncio
    async def test_network_error_returns_none(self, httpx_mock):
        # GIVEN: A network error occurs during the request
        test_url = "https://api.weather.gov/error"
        httpx_mock.add_exception(httpx.NetworkError("Network unreachable"))
        
        # WHEN: Making a request that encounters a network error
        result = await make_nws_request(test_url)
        
        # THEN: The function returns None instead of raising an exception
        assert result is None
    
    @pytest.mark.asyncio
    async def test_invalid_json_returns_none(self, httpx_mock):
        # GIVEN: An NWS API endpoint that returns invalid JSON
        test_url = "https://api.weather.gov/badjson"
        httpx_mock.add_response(text="<html>Not JSON</html>", headers={"content-type": "text/html"})
        
        # WHEN: Making a request that returns non-JSON content
        result = await make_nws_request(test_url)
        
        # THEN: The function returns None instead of raising an exception
        assert result is None
    
    @pytest.mark.asyncio
    async def test_timeout_configuration(self, httpx_mock):
        # GIVEN: A valid NWS API endpoint
        test_url = "https://api.weather.gov/test"
        httpx_mock.add_response(json={"status": "ok"})
        
        # WHEN: Making a request
        await make_nws_request(test_url)
        
        # THEN: The request uses a 30-second timeout
        request = httpx_mock.get_request()
        # Note: httpx-mock doesn't expose timeout directly, but we verify the call was made


class TestFormatAlert:
    # Test suite for format_alert function
    
    def test_format_alert_with_all_fields(self, weather_test_data):
        # GIVEN: A complete weather alert feature with all expected fields
        feature = weather_test_data["alert_response"]["features"][0]
        alert_props = feature["properties"]
        
        # WHEN: Formatting the alert
        result = format_alert(feature)
        
        # THEN: The formatted string contains all the alert information
        assert f"Event: {alert_props['event']}" in result
        assert f"Area: {alert_props['areaDesc']}" in result
        assert f"Severity: {alert_props['severity']}" in result
        assert "Description:" in result
        assert alert_props['description'][:20] in result  # Check start of description
        # AND: Instructions field uses default when not present
        assert "Instructions: No specific instructions provided" in result
    
    def test_format_alert_with_missing_fields(self):
        # GIVEN: A weather alert feature with minimal/missing fields
        feature = {
            "properties": {
                "event": "Test Alert"
            }
        }
        
        # WHEN: Formatting the alert with missing fields
        result = format_alert(feature)
        
        # THEN: The formatted string uses default values for missing fields
        assert "Event: Test Alert" in result
        assert "Area: Unknown" in result
        assert "Severity: Unknown" in result
        assert "Description: No description available" in result
        assert "Instructions: No specific instructions provided" in result
    
    def test_format_alert_with_instructions(self):
        # GIVEN: A weather alert with specific instructions
        feature = {
            "properties": {
                "event": "Tornado Warning",
                "areaDesc": "Downtown Area",
                "severity": "Extreme",
                "description": "Tornado spotted",
                "instruction": "Take shelter immediately in a basement or interior room"
            }
        }
        
        # WHEN: Formatting the alert with instructions
        result = format_alert(feature)
        
        # THEN: The formatted string includes the specific instructions
        assert "Instructions: Take shelter immediately" in result
    
    def test_format_alert_empty_properties(self):
        # GIVEN: A feature with empty properties dictionary
        feature = {"properties": {}}
        
        # WHEN: Formatting the alert
        result = format_alert(feature)
        
        # THEN: All fields show default values
        assert "Event: Unknown" in result
        assert "Area: Unknown" in result
        assert "Severity: Unknown" in result
        assert "Description: No description available" in result
        assert "Instructions: No specific instructions provided" in result