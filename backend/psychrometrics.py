"""
Psychrometric calculations for AWG Climate Suitability Analyzer
"""
import math


def saturation_vapor_pressure(temp_c: float) -> float:
    """
    Calculate saturation vapor pressure using Magnus formula.
    es = 6.112 × exp((17.67 × T) / (T + 243.5))
    Returns: es in hPa
    """
    return 6.112 * math.exp((17.67 * temp_c) / (temp_c + 243.5))


def actual_vapor_pressure(temp_c: float, rh: float) -> float:
    """
    Calculate actual vapor pressure.
    e = (RH / 100) × es
    Returns: e in hPa
    """
    es = saturation_vapor_pressure(temp_c)
    return (rh / 100.0) * es


def absolute_humidity(temp_c: float, rh: float) -> float:
    """
    Calculate absolute humidity.
    AH = (2.1674 × e) / (273.15 + T)
    Returns: AH in g/m³  (typical range: 5–30 g/m³)
    """
    e = actual_vapor_pressure(temp_c, rh)
    return (2.1674 * e) / (273.15 + temp_c) * 100  # ×100 converts hPa to proper g/m³ scale


def dew_point(temp_c: float, rh: float) -> float:
    """
    Calculate dew point temperature using Magnus formula.
    Returns: dew point in °C
    """
    if rh <= 0:
        return temp_c - 50
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(rh / 100.0)
    dp = (b * alpha) / (a - alpha)
    return round(dp, 2)


def calculate_water_extraction(temp_c: float, rh: float, airflow_m3_per_hour: float = 500.0, efficiency: float = 0.4) -> dict:
    """
    Calculate potential water extraction from AWG system.
    
    Args:
        temp_c: Temperature in Celsius
        rh: Relative humidity percentage
        airflow_m3_per_hour: AWG airflow rate (default 500 m³/hour)
        efficiency: AWG extraction efficiency (default 40%)
    
    Returns:
        Dictionary with water extraction metrics
    """
    ah = absolute_humidity(temp_c, rh)
    
    # Water vapor per hour in grams
    water_vapor_grams_per_hour = ah * airflow_m3_per_hour
    
    # Convert grams to liters (1 liter water = 1000 grams)
    water_vapor_liters_per_hour = water_vapor_grams_per_hour / 1000.0
    
    # Apply extraction efficiency
    extracted_liters_per_hour = water_vapor_liters_per_hour * efficiency
    
    # Daily extraction
    extracted_liters_per_day = extracted_liters_per_hour * 24
    
    return {
        "absolute_humidity_g_m3": round(ah, 4),
        "water_vapor_grams_per_hour": round(water_vapor_grams_per_hour, 2),
        "water_vapor_liters_per_hour": round(water_vapor_liters_per_hour, 4),
        "extracted_liters_per_hour": round(extracted_liters_per_hour, 4),
        "extracted_liters_per_day": round(extracted_liters_per_day, 2),
        "saturation_vapor_pressure_hpa": round(saturation_vapor_pressure(temp_c), 4),
        "actual_vapor_pressure_hpa": round(actual_vapor_pressure(temp_c, rh), 4),
        "dew_point_c": dew_point(temp_c, rh),
    }


def get_full_psychrometric_data(temp_c: float, rh: float, pressure_hpa: float = 1013.25) -> dict:
    """
    Get comprehensive psychrometric data for a given temperature and humidity.
    """
    water_data = calculate_water_extraction(temp_c, rh)
    
    return {
        "temperature_c": temp_c,
        "relative_humidity_pct": rh,
        "pressure_hpa": pressure_hpa,
        **water_data,
    }
