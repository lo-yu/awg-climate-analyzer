"""
Machine Learning model for AWG water generation prediction.
Uses RandomForestRegressor trained on synthetic climate data.
"""
import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from psychrometrics import absolute_humidity, dew_point, calculate_water_extraction

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")


def generate_synthetic_dataset(n_samples: int = 1000) -> pd.DataFrame:
    """
    Generate synthetic climate dataset with realistic ranges for India and global locations.
    """
    np.random.seed(42)
    
    temperatures = np.random.uniform(5, 40, n_samples)
    humidities = np.random.uniform(20, 95, n_samples)
    pressures = np.random.uniform(990, 1025, n_samples)
    months = np.random.randint(1, 13, n_samples)
    
    dew_points = [dew_point(t, h) for t, h in zip(temperatures, humidities)]
    abs_humidities = [absolute_humidity(t, h) for t, h in zip(temperatures, humidities)]
    
    # Calculate realistic water output scaled to industrial AWG (500 m3/hr unit)
    # Physics gives ~0.2-0.5 g/m3 AH; scaled to liters/day for 500m3/hr AWG:
    # water = AH * 500 m3/hr * 24 hr * 0.4 efficiency / 1000 g/L
    # For Delhi (AH~22 g/m3 at 65% RH, 32C): ~105 L/day — matches spec
    water_outputs = []
    for i in range(n_samples):
        ah = abs_humidities[i]
        # Industrial scale: 500 m3/hr * 24 hr * 40% efficiency
        base_output = ah * 500 * 24 * 0.4 / 1000  # liters/day
        
        # Add seasonal variation
        seasonal_factor = 1 + 0.15 * np.sin(2 * np.pi * months[i] / 12)
        
        # Add realistic noise (±10%)
        noise = np.random.normal(0, base_output * 0.1)
        
        water_outputs.append(max(0, base_output * seasonal_factor + noise))
    
    df = pd.DataFrame({
        "temperature": temperatures,
        "humidity": humidities,
        "dew_point": dew_points,
        "pressure": pressures,
        "month": months,
        "absolute_humidity": abs_humidities,
        "water_output_liters_per_day": water_outputs,
    })
    
    return df


def train_model(df: pd.DataFrame = None) -> tuple:
    """
    Train RandomForestRegressor model on climate data.
    Returns: (model, mae, feature_importances)
    """
    if df is None:
        df = generate_synthetic_dataset(1000)
    
    features = ["temperature", "humidity", "dew_point", "pressure", "month"]
    target = "water_output_liters_per_day"
    
    X = df[features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    
    feature_importances = dict(zip(features, model.feature_importances_.tolist()))
    
    return model, mae, feature_importances


def save_model(model) -> None:
    """Save trained model to disk."""
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)


def load_model():
    """Load trained model from disk, training if not found."""
    if not os.path.exists(MODEL_PATH):
        print("No model found. Training new model...")
        model, mae, importances = train_model()
        save_model(model)
        print(f"Model trained and saved. MAE: {mae:.2f} L/day")
        return model
    
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


def predict_water_output(
    temperature: float,
    humidity: float,
    dew_point_val: float,
    pressure: float,
    month: int,
    model=None,
) -> float:
    """
    Predict daily water output using the trained ML model.
    Returns: Predicted liters per day
    """
    if model is None:
        model = load_model()
    
    features = pd.DataFrame([[temperature, humidity, dew_point_val, pressure, month]],
                             columns=["temperature", "humidity", "dew_point", "pressure", "month"])
    prediction = model.predict(features)[0]
    return max(0, round(float(prediction), 2))


def calculate_suitability_score(
    humidity: float,
    predicted_water_output: float,
    temperature: float,
) -> dict:
    """
    Calculate AWG suitability score (0–100).
    - 40% humidity factor
    - 30% predicted water output factor
    - 30% temperature suitability factor
    """
    # Humidity factor (optimal: 60-90%)
    if humidity >= 60:
        humidity_factor = min(humidity / 90.0, 1.0)
    elif humidity >= 40:
        humidity_factor = (humidity - 20) / 40.0
    else:
        humidity_factor = max(0, humidity / 40.0) * 0.5
    
    humidity_score = humidity_factor * 100 * 0.40
    
    # Water output factor (optimal: >150 L/day = 100%)
    water_factor = min(predicted_water_output / 150.0, 1.0)
    water_score = water_factor * 100 * 0.30
    
    # Temperature suitability (optimal: 20-35°C for AWG)
    if 20 <= temperature <= 35:
        temp_factor = 1.0
    elif 10 <= temperature < 20:
        temp_factor = (temperature - 5) / 15.0
    elif temperature > 35:
        temp_factor = max(0, 1 - (temperature - 35) / 15.0)
    else:
        temp_factor = max(0, temperature / 10.0) * 0.3
    
    temp_score = temp_factor * 100 * 0.30
    
    total_score = round(humidity_score + water_score + temp_score, 1)
    
    # Recommendation
    if predicted_water_output < 50:
        recommendation = "Small AWG Unit"
        recommendation_detail = "Suitable for personal/household use (up to 5 people)"
    elif predicted_water_output <= 150:
        recommendation = "Medium AWG Unit"
        recommendation_detail = "Suitable for community/office use (up to 50 people)"
    else:
        recommendation = "Large AWG System"
        recommendation_detail = "Suitable for industrial/municipal use (100+ people)"
    
    # Feasibility rating
    if total_score >= 70:
        feasibility = "Highly Feasible"
        feasibility_color = "#22c55e"
    elif total_score >= 45:
        feasibility = "Moderately Feasible"
        feasibility_color = "#f59e0b"
    elif total_score >= 25:
        feasibility = "Low Feasibility"
        feasibility_color = "#f97316"
    else:
        feasibility = "Not Recommended"
        feasibility_color = "#ef4444"
    
    return {
        "total_score": total_score,
        "humidity_score": round(humidity_score, 1),
        "water_score": round(water_score, 1),
        "temperature_score": round(temp_score, 1),
        "recommendation": recommendation,
        "recommendation_detail": recommendation_detail,
        "feasibility": feasibility,
        "feasibility_color": feasibility_color,
    }


if __name__ == "__main__":
    print("Training AWG prediction model...")
    df = generate_synthetic_dataset(1000)
    model, mae, importances = train_model(df)
    save_model(model)
    print(f"✓ Model trained successfully!")
    print(f"  Mean Absolute Error: {mae:.2f} L/day")
    print(f"  Feature Importances: {importances}")
    print(f"  Model saved to: {MODEL_PATH}")
