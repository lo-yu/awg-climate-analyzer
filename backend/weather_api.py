"""
Weather API integration for OpenWeatherMap.
Fetches real-time climate data for AWG analysis.
"""
import os
import httpx
from datetime import datetime
from psychrometrics import dew_point, absolute_humidity

OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
GEOCODING_URL = "http://api.openweathermap.org/geo/1.0/direct"


async def fetch_weather_by_city(city: str, api_key: str) -> dict:
    """
    Fetch weather data for a city by name.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{OPENWEATHER_BASE_URL}/weather",
            params={"q": city, "appid": api_key, "units": "metric"},
        )
        response.raise_for_status()
        return _parse_weather_response(response.json())


async def fetch_weather_by_coords(lat: float, lon: float, api_key: str) -> dict:
    """
    Fetch weather data by latitude/longitude coordinates.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{OPENWEATHER_BASE_URL}/weather",
            params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric"},
        )
        response.raise_for_status()
        return _parse_weather_response(response.json())


async def geocode_city(city: str, api_key: str) -> dict:
    """
    Geocode a city name to coordinates.
    Returns lat/lon for map display.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            GEOCODING_URL,
            params={"q": city, "limit": 1, "appid": api_key},
        )
        response.raise_for_status()
        results = response.json()
        if not results:
            raise ValueError(f"City '{city}' not found")
        return {"lat": results[0]["lat"], "lon": results[0]["lon"], "name": results[0].get("name", city)}


def _parse_weather_response(data: dict) -> dict:
    """
    Parse OpenWeatherMap API response into standardized format.
    """
    temp = data["main"]["temp"]
    rh = data["main"]["humidity"]
    pressure = data["main"]["pressure"]
    
    dp = dew_point(temp, rh)
    ah = absolute_humidity(temp, rh)
    
    return {
        "city": data.get("name", "Unknown"),
        "country": data.get("sys", {}).get("country", ""),
        "latitude": data.get("coord", {}).get("lat", 0),
        "longitude": data.get("coord", {}).get("lon", 0),
        "temperature_c": round(temp, 1),
        "relative_humidity_pct": rh,
        "pressure_hpa": pressure,
        "wind_speed_ms": data.get("wind", {}).get("speed", 0),
        "dew_point_c": dp,
        "absolute_humidity_g_m3": round(ah, 3),
        "weather_description": data.get("weather", [{}])[0].get("description", "").title(),
        "weather_icon": data.get("weather", [{}])[0].get("icon", ""),
        "timestamp": datetime.utcnow().isoformat(),
        "month": datetime.utcnow().month,
        "feels_like_c": round(data["main"].get("feels_like", temp), 1),
        "visibility_m": data.get("visibility", 0),
        "clouds_pct": data.get("clouds", {}).get("all", 0),
    }


def get_mock_weather_data(city: str) -> dict:
    """
    Return realistic mock weather data for demo/fallback use.
    Covers major Indian cities and some global locations.
    """
    mock_data = {
        "delhi": {"temp": 32, "rh": 65, "pressure": 1005, "wind": 3.2, "lat": 28.6139, "lon": 77.2090},
        "mumbai": {"temp": 29, "rh": 82, "pressure": 1010, "wind": 5.1, "lat": 19.0760, "lon": 72.8777},
        "rajasthan": {"temp": 38, "rh": 28, "pressure": 998, "wind": 4.5, "lat": 27.0238, "lon": 74.2179},
        "ladakh": {"temp": 8, "rh": 35, "pressure": 720, "wind": 6.2, "lat": 34.1526, "lon": 77.5770},
        "bangalore": {"temp": 24, "rh": 70, "pressure": 912, "wind": 2.8, "lat": 12.9716, "lon": 77.5946},
        "chennai": {"temp": 31, "rh": 78, "pressure": 1008, "wind": 4.0, "lat": 13.0827, "lon": 80.2707},
        "kolkata": {"temp": 30, "rh": 75, "pressure": 1007, "wind": 3.5, "lat": 22.5726, "lon": 88.3639},
        "hyderabad": {"temp": 28, "rh": 60, "pressure": 1004, "wind": 3.1, "lat": 17.3850, "lon": 78.4867},
    }
    
    key = city.lower().strip()
    data = mock_data.get(key, mock_data["delhi"])
    
    temp = data["temp"]
    rh = data["rh"]
    dp = dew_point(temp, rh)
    ah = absolute_humidity(temp, rh)
    
    return {
        "city": city.title(),
        "country": "IN",
        "latitude": data["lat"],
        "longitude": data["lon"],
        "temperature_c": temp,
        "relative_humidity_pct": rh,
        "pressure_hpa": data["pressure"],
        "wind_speed_ms": data["wind"],
        "dew_point_c": dp,
        "absolute_humidity_g_m3": round(ah, 3),
        "weather_description": "Partly Cloudy",
        "weather_icon": "02d",
        "timestamp": datetime.utcnow().isoformat(),
        "month": datetime.utcnow().month,
        "feels_like_c": temp + 2,
        "visibility_m": 8000,
        "clouds_pct": 40,
        "is_mock": True,
    }
