import os

import requests
from langchain.tools import tool
from langchain_nimble import NimbleSearchTool

search_tool = NimbleSearchTool(max_retries=0)
search_tool._sync_client = search_tool._sync_client.with_options(
    timeout=5,
    max_retries=0,
)


@tool
def google_search_tool(query: str) -> str:
    """Search Google for real-time information.

    Args:
        query: The search query.

    Returns:
        Search results (with source URLs where available).
    """
    try:
        result = search_tool.invoke(
            {
                "query": query,
                "max_results": 3,
                "search_depth": "lite",
            }
        )
        return result if isinstance(result, str) else str(result)
    except Exception as e:
        return f"Search failed: {e}"


@tool
def weather_tool(city: str) -> dict | str:
    """Get real-time weather (temperature, humidity, wind, conditions) for a city.

    Args:
        city: City name, e.g. "Bengaluru" or "London,UK".

    Returns:
        A short dict of weather details, or an error message.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return "Weather API key is missing. Set WEATHER_API_KEY in your .env file."

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=8,
        )
    except requests.RequestException as e:
        return f"Weather request failed: {e}"

    if response.status_code != 200:
        return f"Unable to find weather details for '{city}'."

    data = response.json()
    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature_c": data["main"]["temp"],
        "feels_like_c": data["main"]["feels_like"],
        "humidity_percent": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
        "wind_speed_mps": data["wind"]["speed"],
    }


ALL_TOOLS = [google_search_tool, weather_tool]