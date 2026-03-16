"""
AWG Analysis module - combines weather, psychrometrics, and ML prediction.
"""
from psychrometrics import get_full_psychrometric_data, calculate_water_extraction
from ml_model import predict_water_output, calculate_suitability_score, load_model

# Singleton model instance
_model = None


def get_model():
    global _model
    if _model is None:
        _model = load_model()
    return _model


def run_full_analysis(weather_data: dict) -> dict:
    """
    Run complete AWG analysis for a given location's weather data.
    
    Steps:
    1. Calculate psychrometric values
    2. Feed features into ML model
    3. Predict daily water generation
    4. Calculate suitability score
    5. Provide AWG recommendation
    """
    temp = weather_data["temperature_c"]
    rh = weather_data["relative_humidity_pct"]
    pressure = weather_data["pressure_hpa"]
    dp = weather_data["dew_point_c"]
    month = weather_data["month"]
    
    # Step 1: Psychrometric calculations
    psychro = get_full_psychrometric_data(temp, rh, pressure)
    
    # Step 2: ML prediction
    model = get_model()
    predicted_output = predict_water_output(
        temperature=temp,
        humidity=rh,
        dew_point_val=dp,
        pressure=pressure,
        month=month,
        model=model,
    )
    
    # Step 3: Suitability score
    suitability = calculate_suitability_score(rh, predicted_output, temp)
    
    # Step 4: Water extraction details (physics-based)
    extraction = calculate_water_extraction(temp, rh)
    
    # Step 5: Build comprehensive result
    return {
        "location": {
            "city": weather_data.get("city", "Unknown"),
            "country": weather_data.get("country", ""),
            "latitude": weather_data.get("latitude", 0),
            "longitude": weather_data.get("longitude", 0),
        },
        "weather": {
            "temperature_c": temp,
            "relative_humidity_pct": rh,
            "pressure_hpa": pressure,
            "wind_speed_ms": weather_data.get("wind_speed_ms", 0),
            "dew_point_c": dp,
            "feels_like_c": weather_data.get("feels_like_c", temp),
            "weather_description": weather_data.get("weather_description", ""),
            "weather_icon": weather_data.get("weather_icon", ""),
            "timestamp": weather_data.get("timestamp", ""),
            "clouds_pct": weather_data.get("clouds_pct", 0),
        },
        "psychrometrics": {
            "absolute_humidity_g_m3": psychro["absolute_humidity_g_m3"],
            "saturation_vapor_pressure_hpa": psychro["saturation_vapor_pressure_hpa"],
            "actual_vapor_pressure_hpa": psychro["actual_vapor_pressure_hpa"],
            "dew_point_c": dp,
        },
        "water_extraction": {
            "airflow_m3_per_hour": 500,
            "efficiency_pct": 40,
            "water_vapor_grams_per_hour": extraction["water_vapor_grams_per_hour"],
            "extracted_liters_per_hour": extraction["extracted_liters_per_hour"],
            "extracted_liters_per_day_physics": extraction["extracted_liters_per_day"],
        },
        "ml_prediction": {
            "predicted_water_output_liters_per_day": predicted_output,
            "model_type": "RandomForestRegressor",
            "features_used": ["temperature", "humidity", "dew_point", "pressure", "month"],
        },
        "suitability": suitability,
        "is_mock": weather_data.get("is_mock", False),
    }


def get_historical_comparison(city: str) -> list:
    """
    Generate synthetic monthly AWG potential data for trend visualization.
    Represents typical annual variation for a given city type.
    """
    import numpy as np
    
    # City profiles for India
    profiles = {
        "delhi": {"base_temp": 25, "temp_var": 12, "base_rh": 60, "rh_var": 25},
        "mumbai": {"base_temp": 28, "temp_var": 4, "base_rh": 78, "rh_var": 15},
        "rajasthan": {"base_temp": 30, "temp_var": 15, "base_rh": 35, "rh_var": 25},
        "ladakh": {"base_temp": 5, "temp_var": 15, "base_rh": 35, "rh_var": 15},
        "bangalore": {"base_temp": 24, "temp_var": 4, "base_rh": 68, "rh_var": 20},
        "chennai": {"base_temp": 30, "temp_var": 5, "base_rh": 74, "rh_var": 18},
    }
    
    profile = profiles.get(city.lower(), profiles["delhi"])
    months = list(range(1, 13))
    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    
    monthly_data = []
    model = get_model()
    
    for m in months:
        # Seasonal variation using sine wave
        season_factor = np.sin(2 * np.pi * (m - 3) / 12)
        
        temp = profile["base_temp"] + profile["temp_var"] * season_factor
        rh = profile["base_rh"] + profile["rh_var"] * (0.5 + 0.5 * season_factor)
        rh = min(95, max(20, rh))
        
        dp = sum([
            calculate_water_extraction(temp, rh)["dew_point_c"] 
            if False else 0
        ]) or (temp - ((100 - rh) / 5))
        
        predicted = predict_water_output(
            temperature=temp,
            humidity=rh,
            dew_point_val=dp,
            pressure=1013,
            month=m,
            model=model,
        )
        
        monthly_data.append({
            "month": month_names[m - 1],
            "month_num": m,
            "avg_temperature_c": round(temp, 1),
            "avg_humidity_pct": round(rh, 1),
            "predicted_water_liters": round(predicted, 1),
        })
    
    return monthly_data
