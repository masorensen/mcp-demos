import pytest

from mcp_server.tools.weather import get_alerts, get_forecast
from tests.helpers import mock_nws_request, assert_contains_all, create_forecast_periods


class TestGetAlerts:
    # Test suite for get_alerts MCP tool
    
    @pytest.mark.asyncio
    async def test_get_alerts_with_active_alerts(self, weather_test_data):
        # GIVEN: A state with active weather alerts
        state = "NY"
        alert_data = weather_test_data["alert_response"]["features"][0]["properties"]
        
        # WHEN: Requesting alerts for the state with mocked API response
        async with mock_nws_request(weather_test_data["alert_response"]) as mock_request:
            result = await get_alerts(state)
            
            # THEN: The tool returns formatted alert information with the expected data
            assert_contains_all(result,
                f"Event: {alert_data['event']}",
                f"Area: {alert_data['areaDesc']}", 
                f"Severity: {alert_data['severity']}",
                alert_data['description'][:20]  # Check first part of description
            )
            # AND: The correct API endpoint was called
            mock_request.assert_called_once_with(
                f"https://api.weather.gov/alerts/active/area/{state}"
            )
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("state,response,expected", [
        ("CA", {"features": []}, "No active alerts for this state."),
        ("TX", None, "Unable to fetch alerts or no alerts found."),
        ("FL", {"status": "ok", "data": []}, "Unable to fetch alerts or no alerts found."),
    ])
    async def test_get_alerts_edge_cases(self, state, response, expected):
        # GIVEN: Various API response scenarios
        # WHEN: Requesting alerts with different responses
        async with mock_nws_request(response) as mock_request:
            result = await get_alerts(state)
            
            # THEN: The tool handles each case appropriately
            assert result == expected
    
    @pytest.mark.asyncio
    async def test_get_alerts_multiple_alerts(self, weather_test_data):
        # GIVEN: A state with multiple active alerts
        state = "OK"
        alerts = weather_test_data["multi_alert_response"]["features"]
        
        # WHEN: Requesting alerts with multiple alerts
        async with mock_nws_request(weather_test_data["multi_alert_response"]) as mock_request:
            result = await get_alerts(state)
            
            # THEN: All alerts are included with proper formatting
            assert_contains_all(result,
                f"Event: {alerts[0]['properties']['event']}",
                f"Event: {alerts[1]['properties']['event']}",
                alerts[0]['properties']['areaDesc'],
                alerts[1]['properties']['areaDesc'],
                "---"  # Alert separator
            )


class TestGetForecast:
    # Test suite for get_forecast MCP tool
    
    @pytest.mark.asyncio
    async def test_get_forecast_success(self, weather_test_data):
        # GIVEN: Valid coordinates for a location
        lat, lon = 40.7128, -74.0060
        forecast_data = weather_test_data["forecast_response"]["properties"]["periods"]
        
        # WHEN: Requesting forecast with successful API responses
        responses = [weather_test_data["points_response"], weather_test_data["forecast_response"]]
        async with mock_nws_request(side_effect=responses) as mock_request:
            result = await get_forecast(lat, lon)
            
            # THEN: The forecast is properly formatted with dynamic data
            today = forecast_data[0]
            tonight = forecast_data[1]
            assert_contains_all(result,
                "Today:",
                f"Temperature: {today['temperature']}°F",
                f"Wind: {today['windSpeed']} {today['windDirection']}",
                "Tonight:",
                f"Temperature: {tonight['temperature']}°F"
            )
            # AND: Both API endpoints were called correctly
            assert mock_request.call_count == 2
            mock_request.assert_any_call(f"https://api.weather.gov/points/{lat},{lon}")
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("points_response,forecast_response,expected_error", [
        (None, None, "Unable to fetch forecast data for this location."),
        ({"properties": {"forecast": "url"}}, None, "Unable to fetch detailed forecast."),
    ])
    async def test_get_forecast_api_failures(self, points_response, forecast_response, expected_error):
        # GIVEN: Various API failure scenarios
        lat, lon = 40.7128, -74.0060
        
        # WHEN: API calls fail at different stages
        if points_response is None:
            async with mock_nws_request(points_response) as mock_request:
                result = await get_forecast(lat, lon)
        else:
            async with mock_nws_request(side_effect=[points_response, forecast_response]) as mock_request:
                result = await get_forecast(lat, lon)
        
        # THEN: Appropriate error messages are returned
        assert result == expected_error
    
    @pytest.mark.asyncio
    async def test_get_forecast_many_periods(self, weather_test_data):
        # GIVEN: A forecast with many periods (14 periods)
        lat, lon = 35.0, -120.0
        extended_forecast = {
            "properties": {"periods": create_forecast_periods(14)}
        }
        
        # WHEN: Requesting forecast with extended periods
        responses = [weather_test_data["points_response"], extended_forecast]
        async with mock_nws_request(side_effect=responses) as mock_request:
            result = await get_forecast(lat, lon)
            
            # THEN: Only the first 7 periods are included
            assert "Period 1:" in result
            assert "Period 7:" in result
            assert "Period 8:" not in result
            # AND: Proper separation between periods
            assert result.count("---") == 6  # 6 separators for 7 periods
    
    @pytest.mark.asyncio
    async def test_get_forecast_coordinate_formatting(self, weather_test_data):
        # GIVEN: Edge case coordinates with many decimal places
        lat, lon = 64.0685, -141.0234
        
        # WHEN: Requesting forecast
        responses = [weather_test_data["points_response"], weather_test_data["forecast_response"]]
        async with mock_nws_request(side_effect=responses) as mock_request:
            result = await get_forecast(lat, lon)
            
            # THEN: Coordinates are properly formatted in API calls
            mock_request.assert_any_call(f"https://api.weather.gov/points/{lat},{lon}")
            assert "Temperature:" in result