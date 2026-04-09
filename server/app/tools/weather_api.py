"""Weather API tool — fetches current weather data."""

from __future__ import annotations

import httpx
import json
import logging
from langchain_core.tools import tool
from app.config import settings
from app.retry import with_retry

logger = logging.getLogger(__name__)

MOCK_WEATHER = {
    "tokyo":    {"city": "Tokyo",    "country": "JP", "temp_celsius": 12.3, "feels_like": 10.1, "humidity": 55, "description": "Partly cloudy",    "wind_speed_kmh": 15.2, "visibility_km": 10},
    "london":   {"city": "London",   "country": "GB", "temp_celsius":  8.7, "feels_like":  5.2, "humidity": 78, "description": "Light rain",       "wind_speed_kmh": 22.4, "visibility_km":  7},
    "new york": {"city": "New York", "country": "US", "temp_celsius":  6.1, "feels_like":  2.8, "humidity": 62, "description": "Clear sky",        "wind_speed_kmh": 18.7, "visibility_km": 15},
    "paris":    {"city": "Paris",    "country": "FR", "temp_celsius": 10.5, "feels_like":  7.9, "humidity": 70, "description": "Overcast clouds",  "wind_speed_kmh": 12.1, "visibility_km":  9},
    "sydney":   {"city": "Sydney",   "country": "AU", "temp_celsius": 24.8, "feels_like": 26.1, "humidity": 65, "description": "Sunny",            "wind_speed_kmh":  8.3, "visibility_km": 20},
}

DEFAULT_MOCK = {
    "country": "Unknown", "temp_celsius": 15.0, "feels_like": 13.5,
    "humidity": 60, "description": "Moderate conditions",
    "wind_speed_kmh": 14.0, "visibility_km": 10,
}


@with_retry(max_retries=3, base_delay=1.0)
async def _fetch_weather(city: str) -> dict:
    """Fetch from OpenWeatherMap or return mock data if no API key."""
    api_key = settings.openweathermap_api_key

    if not api_key:
        city_lower = city.strip().lower()
        if city_lower in MOCK_WEATHER:
            return MOCK_WEATHER[city_lower]
        return {"city": city, **DEFAULT_MOCK}

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    return {
        "city": data.get("name", city),
        "country": data["sys"]["country"],
        "temp_celsius": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "wind_speed_kmh": round(data["wind"]["speed"] * 3.6, 1),
        "visibility_km": round(data.get("visibility", 10000) / 1000, 1),
    }


@tool
async def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: Name of the city (e.g., "Tokyo", "London", "New York").
    """
    logger.info(f"[Weather] {city}")
    result = await _fetch_weather(city)

    if isinstance(result, dict) and result.get("error"):
        return json.dumps(result)

    return json.dumps(result, indent=2)
