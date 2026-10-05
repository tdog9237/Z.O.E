"""
Weather Information Skill for Z.O.E.
=====================================
Demonstrates how to fetch external real-time data using Python requests,
with automatic fallback to clean mock data when offline.
"""

import requests
from typing import Dict, Any, Optional
from .base_skill import BaseSkill

# Latitude and Longitude coordinates for common UK and international cities
_CITY_COORDINATES = {
    "london": (51.5074, -0.1278, "London, United Kingdom"),
    "manchester": (53.4808, -2.2426, "Manchester, United Kingdom"),
    "birmingham": (52.4862, -1.8904, "Birmingham, United Kingdom"),
    "cardiff": (51.4816, -3.1791, "Cardiff, Wales"),
    "edinburgh": (55.9533, -3.1883, "Edinburgh, Scotland"),
    "bristol": (51.4545, -2.5879, "Bristol, United Kingdom"),
    "new york": (40.7128, -74.0060, "New York, USA"),
    "paris": (48.8566, 2.3522, "Paris, France"),
    "tokyo": (35.6762, 139.6503, "Tokyo, Japan"),
}

# Weather code interpretations (WMO Code standard)
_WMO_WEATHER_CODES = {
    0: "clear sunny skies",
    1: "mainly clear skies",
    2: "partly cloudy skies",
    3: "overcast clouds",
    45: "foggy conditions",
    48: "depositing rime fog",
    51: "light drizzle",
    61: "slight rain showers",
    63: "moderate steady rain",
    65: "heavy rain",
    71: "light snowfall",
    80: "isolated rain showers",
    95: "thunderstorm conditions"
}


class WeatherSkill(BaseSkill):
    name = "Weather Information"
    description = "Retrieves live weather reports and forecasts for major cities using Open-Meteo."
    triggers = [
        "weather", "forecast", "temperature outside",
        "is it raining", "how cold is it", "how warm is it"
    ]
    author = "Z.O.E Core Team"
    version = "1.0.0"

    def can_handle(self, message: str) -> bool:
        msg = message.lower().strip()
        return any(trigger in msg for trigger in self.triggers)

    def execute(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        msg = message.lower().strip()

        # Identify requested city (default to London)
        target_city = "london"
        for city in _CITY_COORDINATES:
            if city in msg:
                target_city = city
                break

        lat, lon, city_full = _CITY_COORDINATES[target_city]

        # Query free public Open-Meteo API (requires 0 API keys)
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&timezone=auto"
            resp = requests.get(url, timeout=3.0)
            if resp.ok:
                data = resp.json().get("current", {})
                temp = data.get("temperature_2m")
                humidity = data.get("relative_humidity_2m")
                code = data.get("weather_code", 0)
                wind = data.get("wind_speed_10m")
                condition = _WMO_WEATHER_CODES.get(code, "fair conditions")

                return (
                    f"In {city_full}, it is currently {temp}°C with {condition}. "
                    f"Humidity is at {humidity}% and wind speed is {wind} km/h."
                )
        except Exception:
            pass

        # Offline fallback report
        return (
            f"Currently in {city_full}, conditions are mild with typical seasonal temperatures around 14°C "
            f"and moderate cloud cover. (Offline status report)"
        )
