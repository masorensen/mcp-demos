import os
import requests
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def get_weather(location: str) -> str:
    """
    Fetches the current weather for a given location.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "OpenWeather API key is not set."

    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code != 200:
        return f"Error fetching weather data: {response.text}"

    data = response.json()
    weather = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    return f"The current weather in {location} is {weather} with a temperature of {temp}°C."
