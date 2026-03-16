"""
AWG Climate Suitability Analyzer - FastAPI Backend
Main application entry point with all API endpoints.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from weather_api import fetch_weather_by_city, fetch_weather_by_coords, get_mock_weather_data
from awg_analysis import run_full_analysis, get_historical_comparison
from ml_model import load_model

# Load API key from environment
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

app = FastAPI(
    title="AWG Climate Suitability Analyzer",
    description="Analyzes climate data to predict Atmospheric Water Generator (AWG) performance.",
    version="1.0.0",
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pre-load ML model on startup
@app.on_event("startup")
async def startup_event():
    print("Loading ML model...")
    load_model()
    api_status = "LIVE (OpenWeatherMap)" if OPENWEATHER_API_KEY else "DEMO (mock data)"
    print(f"Weather data: {api_status}")
    print("✓ AWG Climate Analyzer ready!")

# ─── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "message": "AWG Climate Suitability Analyzer API",
        "version": "1.0.0",
        "endpoints": ["/weather", "/awg-analysis", "/prediction", "/historical"],
    }

@app.get("/weather")
async def get_weather(
    city: Optional[str] = Query(None, description="City name"),
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
):
    """
    Fetch real-time weather data for a location.
    Accepts either city name OR lat/lon coordinates.
    Falls back to mock data if no API key is configured.
    """
    if not city and (lat is None or lon is None):
        raise HTTPException(status_code=400, detail="Provide either 'city' or both 'lat' and 'lon'")
    
    if not OPENWEATHER_API_KEY:
        # Use mock data for demo
        location = city or f"{lat},{lon}"
        data = get_mock_weather_data(city or "delhi")
        if lat and lon:
            data["latitude"] = lat
            data["longitude"] = lon
            data["city"] = f"Lat: {lat:.2f}, Lon: {lon:.2f}"
        return data
    
    try:
        if city:
            return await fetch_weather_by_city(city, OPENWEATHER_API_KEY)
        else:
            return await fetch_weather_by_coords(lat, lon, OPENWEATHER_API_KEY)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Weather API error: {str(e)}")


@app.get("/awg-analysis")
async def get_awg_analysis(
    city: Optional[str] = Query(None),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
):
    """
    Return psychrometric calculations and AWG water potential.
    Combines weather data with physics-based calculations.
    """
    weather_data = await get_weather(city=city, lat=lat, lon=lon)
    
    from psychrometrics import get_full_psychrometric_data, calculate_water_extraction
    
    temp = weather_data["temperature_c"]
    rh = weather_data["relative_humidity_pct"]
    pressure = weather_data["pressure_hpa"]
    
    psychro = get_full_psychrometric_data(temp, rh, pressure)
    extraction = calculate_water_extraction(temp, rh)
    
    return {
        "location": {
            "city": weather_data.get("city"),
            "latitude": weather_data.get("latitude"),
            "longitude": weather_data.get("longitude"),
        },
        "weather": {
            "temperature_c": temp,
            "relative_humidity_pct": rh,
            "pressure_hpa": pressure,
            "wind_speed_ms": weather_data.get("wind_speed_ms"),
            "dew_point_c": weather_data.get("dew_point_c"),
        },
        "psychrometrics": psychro,
        "water_extraction": extraction,
    }


@app.get("/prediction")
async def get_prediction(
    city: Optional[str] = Query(None),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
):
    """
    Return ML prediction and AWG suitability score.
    Full pipeline: weather → psychrometrics → ML → score → recommendation.
    """
    weather_data = await get_weather(city=city, lat=lat, lon=lon)
    analysis = run_full_analysis(weather_data)
    return analysis


@app.get("/historical")
async def get_historical(city: str = Query("delhi", description="City for historical trends")):
    """
    Return monthly historical AWG potential data for trend charts.
    """
    data = get_historical_comparison(city)
    return {"city": city, "monthly_data": data}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": True}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
