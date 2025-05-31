from contextlib import asynccontextmanager
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, patch
import pytest
from faker import Faker
from datetime import datetime, timedelta
import random


@asynccontextmanager
async def mock_nws_request(return_value: Optional[Dict[str, Any]] = None, side_effect=None):
    # mock make_nws_request so we can do context manager testing
    with patch('mcp_server.tools.weather.make_nws_request', new_callable=AsyncMock) as mock:
        if side_effect is not None:
            mock.side_effect = side_effect
        else:
            mock.return_value = return_value
        yield mock


@pytest.fixture(scope="module")
def weather_test_data():
    """Generate realistic weather test data using Faker."""
    fake = Faker()
    fake.seed_instance(12345)  # Seed for consistent test data
    random.seed(12345)  # Also seed random for consistent choices
    
    # Weather event types and severities based on NWS standards
    weather_events = [
        "Winter Storm Warning",
        "Tornado Warning", 
        "Severe Thunderstorm Warning",
        "Flood Warning",
        "Heat Advisory",
        "Wind Advisory",
        "Winter Weather Advisory"
    ]
    
    severities = ["Extreme", "Severe", "Moderate", "Minor"]
    certainties = ["Observed", "Likely", "Possible", "Unlikely"]
    urgencies = ["Immediate", "Expected", "Future", "Past"]
    
    # Generate dates
    effective_date = fake.date_time_between(start_date='-1d', end_date='now')
    expires_date = effective_date + timedelta(hours=random.randint(6, 48))
    
    # Generate realistic weather descriptions
    def generate_weather_description(event_type):
        if "Winter Storm" in event_type:
            return f"Heavy snow expected. Total snow accumulations of {random.randint(8, 18)} to {random.randint(20, 30)} inches."
        elif "Tornado" in event_type:
            return f"Tornado {random.choice(['spotted', 'detected by radar'])} moving {random.choice(['northeast', 'east', 'southeast'])} at {random.randint(25, 45)} mph."
        elif "Thunderstorm" in event_type:
            return f"Large hail up to {random.choice(['quarter', 'golf ball', 'tennis ball'])} size and damaging winds up to {random.randint(60, 80)} mph possible."
        elif "Flood" in event_type:
            return f"Flash flooding {random.choice(['likely', 'expected', 'occurring'])} in low-lying areas. {random.randint(2, 6)} inches of rain expected."
        else:
            return fake.sentence(nb_words=12)
    
    # Generate temperature and wind data
    def generate_temperature():
        return random.randint(20, 95)
    
    def generate_wind_speed():
        return f"{random.randint(5, 25)} mph"
    
    def generate_wind_direction():
        return random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])
    
    # Generate realistic county/area names
    def generate_area_desc():
        return f"{fake.city()} {random.choice(['County', 'Counties', 'Metro Area', 'and surrounding areas'])}"
    
    # one weather data object to rule them all
    primary_event = random.choice(weather_events)
    
    return {
        "alert_response": {
            "features": [
                {
                    "properties": {
                        "event": primary_event,
                        "headline": f"{primary_event} issued {effective_date.strftime('%B %d at %I:%M%p %Z')}",
                        "description": generate_weather_description(primary_event),
                        "severity": random.choice(severities),
                        "certainty": random.choice(certainties),
                        "urgency": random.choice(urgencies),
                        "effective": effective_date.isoformat(),
                        "expires": expires_date.isoformat(),
                        "areaDesc": generate_area_desc()
                    }
                }
            ]
        },
        "forecast_response": {
            "properties": {
                "periods": [
                    {
                        "number": 1,
                        "name": "Today",
                        "temperature": generate_temperature(),
                        "temperatureUnit": "F",
                        "windSpeed": generate_wind_speed(),
                        "windDirection": generate_wind_direction(),
                        "shortForecast": random.choice(["Partly Cloudy", "Mostly Sunny", "Cloudy", "Chance of Rain", "Clear"]),
                        "detailedForecast": fake.paragraph(nb_sentences=2)
                    },
                    {
                        "number": 2,
                        "name": "Tonight",
                        "temperature": generate_temperature() - random.randint(10, 20),
                        "temperatureUnit": "F",
                        "windSpeed": generate_wind_speed(),
                        "windDirection": generate_wind_direction(),
                        "shortForecast": random.choice(["Mostly Clear", "Partly Cloudy", "Cloudy", "Fog"]),
                        "detailedForecast": fake.paragraph(nb_sentences=2)
                    }
                ]
            }
        },
        "points_response": {
            "properties": {
                "forecast": f"https://api.weather.gov/gridpoints/{fake.state_abbr()}/{random.randint(1, 100)},{random.randint(1, 100)}/forecast"
            }
        },
        "multi_alert_response": {
            "features": [
                {
                    "properties": {
                        "event": "Tornado Warning",
                        "areaDesc": generate_area_desc(),
                        "severity": "Extreme",
                        "description": generate_weather_description("Tornado Warning")
                    }
                },
                {
                    "properties": {
                        "event": "Flood Warning",
                        "areaDesc": generate_area_desc(),
                        "severity": "Severe",
                        "description": generate_weather_description("Flood Warning")
                    }
                }
            ]
        }
    }


def assert_contains_all(text: str, *substrings: str):
    """Assert that text contains all provided substrings."""
    for substring in substrings:
        assert substring in text, f"Expected '{substring}' in text but not found"


def create_forecast_periods(count: int, base_temp: int = 40) -> list:
    """Create a list of forecast periods for testing."""
    fake = Faker()
    periods = []
    
    for i in range(count):
        temp = base_temp + (i * 5) + random.randint(-3, 3)
        periods.append({
            "number": i + 1,
            "name": f"Period {i + 1}",
            "temperature": temp,
            "temperatureUnit": "F",
            "windSpeed": f"{5 + i + random.randint(0, 5)} mph",
            "windDirection": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
            "shortForecast": random.choice([f"Weather {i + 1}", "Clear", "Cloudy", "Rainy", "Sunny"]),
            "detailedForecast": f"{fake.sentence()} {fake.sentence()}"
        })
    
    return periods