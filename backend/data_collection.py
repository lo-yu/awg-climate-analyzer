import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import json

# Configuration for regions to analyze
REGIONS = [
    {"name": "Phoenix, USA", "lat": 33.4484, "lon": -112.0742, "region_code": "phoenix_usa"},
    {"name": "Cairo, Egypt", "lat": 30.0444, "lon": 31.2357, "region_code": "cairo_egypt"},
    {"name": "New Delhi, India", "lat": 28.7041, "lon": 77.1025, "region_code": "delhi_india"},
    {"name": "Las Vegas, USA", "lat": 36.1699, "lon": -115.1398, "region_code": "vegas_usa"},
    {"name": "Dubai, UAE", "lat": 25.2048, "lon": 55.2708, "region_code": "dubai_uae"},
    {"name": "Beijing, China", "lat": 39.9042, "lon": 116.4074, "region_code": "beijing_china"},
    {"name": "São Paulo, Brazil", "lat": -23.5505, "lon": -46.6333, "region_code": "sao_paulo_brazil"},
    {"name": "Sydney, Australia", "lat": -33.8688, "lon": 151.2093, "region_code": "sydney_australia"},
    {"name": "Stockholm, Sweden", "lat": 59.3293, "lon": 18.0686, "region_code": "stockholm_sweden"},
    {"name": "Cape Town, South Africa", "lat": -33.9249, "lon": 18.4241, "region_code": "cape_town_sa"},
]

def fetch_nasa_power_data(lat, lon, region_name):
    """
    Fetch historical climate data from NASA POWER API (free, no API key needed)
    Returns: humidity, temperature, and other relevant metrics
    """
    try:
        # NASA POWER API endpoint
        base_url = "https://power.larc.nasa.gov/api/v1/monthly"
        
        params = {
            "start": "2020",
            "end": "2023",
            "latitude": lat,
            "longitude": lon,
            "community": "RE",
            "parameters": "ALLSKY_SFC_SW_DWN,T2M,RH2M,PRECTOTCORR",  # Solar, Temp, Humidity, Precipitation
            "format": "JSON"
        }
        
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant parameters
        if "properties" in data and "parameter" in data["properties"]:
            params_data = data["properties"]["parameter"]
            
            monthly_data = []
            if "RH2M" in params_data and "T2M" in params_data:
                rh_data = params_data["RH2M"]
                temp_data = params_data["T2M"]
                
                for month_key in rh_data.keys():
                    monthly_data.append({
                        "month": month_key,
                        "humidity": rh_data[month_key],
                        "temperature": temp_data[month_key]
                    })
            
            return monthly_data
        
        return None
    
    except Exception as e:
        print(f"Error fetching NASA data for {region_name}: {str(e)}")
        return None


def fetch_openweather_data(lat, lon, region_name):
    """
    Fetch current climate data from OpenWeatherMap
    Free tier provides some historical data
    """
    try:
        # Using free API (limited to current/forecast data)
        api_key = os.getenv("OPENWEATHER_API_KEY", "demo")  # Replace with actual key
        
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "temp": data.get("main", {}).get("temp"),
            "humidity": data.get("main", {}).get("humidity"),
            "pressure": data.get("main", {}).get("pressure"),
            "description": data.get("weather", [{}])[0].get("description")
        }
    
    except Exception as e:
        print(f"Error fetching OpenWeather data for {region_name}: {str(e)}")
        return None


def save_climate_data(all_data, filename="climate_data.json"):
    """Save collected data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(all_data, f, indent=2)
    print(f"Data saved to {filename}")


def collect_all_regions_data():
    """Collect climate data for all regions"""
    all_data = {}
    
    print("Collecting climate data from NASA POWER API...")
    for region in REGIONS:
        print(f"\nFetching data for {region['name']}...")
        
        nasa_data = fetch_nasa_power_data(region["lat"], region["lon"], region["name"])
        weather_data = fetch_openweather_data(region["lat"], region["lon"], region["name"])
        
        all_data[region["region_code"]] = {
            "name": region["name"],
            "latitude": region["lat"],
            "longitude": region["lon"],
            "nasa_monthly_data": nasa_data,
            "current_weather": weather_data,
            "collected_at": datetime.now().isoformat()
        }
    
    save_climate_data(all_data)
    return all_data


if __name__ == "__main__":
    collect_all_regions_data()