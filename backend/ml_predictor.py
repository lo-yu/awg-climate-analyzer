import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pickle
from datetime import datetime

class AWGWaterProductionPredictor:
    """
    Machine Learning model to predict AWG water production
    based on climate conditions
    """
    
    def __init__(self):
        self.humidity_model = None
        self.temp_model = None
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_training_data(self, climate_data_file="climate_data.json"):
        """
        Prepare data for ML model training
        Creates synthetic training data based on climate patterns
        """
        with open(climate_data_file, 'r') as f:
            climate_data = json.load(f)
        
        X = []  # Features: [avg_humidity, temp, season_factor, humidity_variance]
        y_production = []  # Target: estimated water production (liters/day)
        
        for region_code, region_data in climate_data.items():
            monthly_data = region_data.get("nasa_monthly_data", [])
            
            if not monthly_data:
                continue
            
            humidities = [d["humidity"] for d in monthly_data if d["humidity"]]
            temperatures = [d["temperature"] for d in monthly_data if d["temperature"]]
            
            if not humidities or not temperatures:
                continue
            
            # Create features for each month
            for i, month_data in enumerate(monthly_data):
                humidity = month_data.get("humidity", 0)
                temperature = month_data.get("temperature", 0)
                
                if humidity > 0 and temperature > -50:  # Valid data
                    season_factor = np.sin(2 * np.pi * (i + 1) / 12)  # Seasonal component
                    humidity_variance = np.std(humidities) if len(humidities) > 1 else 0
                    
                    # Normalize features
                    features = [humidity, temperature, season_factor, humidity_variance]
                    X.append(features)
                    
                    # Estimate water production (simplified model)
                    # Base: humidity-dependent, temperature adjusted
                    if 40 <= humidity <= 80:
                        base_production = 10
                    elif 20 <= humidity < 40:
                        base_production = 5
                    elif humidity > 80:
                        base_production = 8
                    else:
                        base_production = 2
                    
                    # Temperature adjustment
                    if 15 <= temperature <= 40:
                        temp_factor = 1.0
                    elif temperature < 15:
                        temp_factor = 0.7
                    else:
                        temp_factor = 0.8
                    
                    production = base_production * temp_factor + np.random.normal(0, 0.5)
                    production = max(0, production)  # No negative production
                    y_production.append(production)
        
        return np.array(X), np.array(y_production)
    
    def train(self, climate_data_file="climate_data.json"):
        """Train the ML models"""
        print("Preparing training data...")
        X, y = self.prepare_training_data(climate_data_file)
        
        if len(X) == 0:
            print("No data available for training")
            return False
        
        print(f"Training data: {len(X)} samples")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Random Forest model
        print("Training Random Forest model...")
        self.humidity_model = RandomForestRegressor(
            n_estimators=50,
            max_depth=10,
            random_state=42
        )
        self.humidity_model.fit(X_scaled, y)
        
        self.is_trained = True
        print("Model training complete!")
        return True
    
    def predict_production(self, humidity: float, temperature: float, 
                          season_factor: float = 0, humidity_variance: float = 0) -> dict:
        """
        Predict AWG water production for given conditions
        
        Args:
            humidity: relative humidity (0-100%)
            temperature: temperature in Celsius
            season_factor: seasonal adjustment (-1 to 1)
            humidity_variance: variance in humidity
        
        Returns:
            Dictionary with prediction and confidence
        """
        if not self.is_trained:
            return {"error": "Model not trained yet"}
        
        features = np.array([[humidity, temperature, season_factor, humidity_variance]])
        features_scaled = self.scaler.transform(features)
        
        prediction = self.humidity_model.predict(features_scaled)[0]
        prediction = max(0, prediction)  # Ensure non-negative
        
        # Confidence based on input validity
        confidence = 1.0
        if humidity < 20 or humidity > 100:
            confidence -= 0.2
        if temperature < -10 or temperature > 60:
            confidence -= 0.2
        
        return {
            "predicted_production_liters_per_day": round(prediction, 2),
            "confidence_level": round(max(0, confidence), 2),
            "conditions": {
                "humidity": humidity,
                "temperature": temperature,
                "season_factor": season_factor
            }
        }
    
    def predict_seasonal_production(self, region_code: str, climate_data_file="climate_data.json") -> dict:
        """
        Predict water production for each month of the year
        """
        if not self.is_trained:
            return {"error": "Model not trained yet"}
        
        with open(climate_data_file, 'r') as f:
            climate_data = json.load(f)
        
        if region_code not in climate_data:
            return {"error": "Region not found"}
        
        monthly_data = climate_data[region_code].get("nasa_monthly_data", [])
        
        if not monthly_data:
            return {"error": "No climate data for region"}
        
        seasonal_predictions = []
        
        for i, month_data in enumerate(monthly_data):
            humidity = month_data.get("humidity", 0)
            temperature = month_data.get("temperature", 0)
            season_factor = np.sin(2 * np.pi * (i + 1) / 12)
            
            if humidity > 0:
                prediction = self.predict_production(humidity, temperature, season_factor)
                prediction["month"] = i + 1
                seasonal_predictions.append(prediction)
        
        # Calculate annual average
        productions = [p["predicted_production_liters_per_day"] for p in seasonal_predictions]
        annual_avg = np.mean(productions) if productions else 0
        annual_total = sum(productions)
        
        return {
            "region": region_code,
            "monthly_predictions": seasonal_predictions,
            "annual_average_per_day": round(annual_avg, 2),
            "annual_total_liters": round(annual_total, 0)
        }
    
    def save_model(self, filepath="awg_model.pkl"):
        """Save trained model"""
        if self.is_trained:
            with open(filepath, 'wb') as f:
                pickle.dump({
                    'model': self.humidity_model,
                    'scaler': self.scaler
                }, f)
            print(f"Model saved to {filepath}")
    
    def load_model(self, filepath="awg_model.pkl"):
        """Load trained model"""
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.humidity_model = data['model']
                self.scaler = data['scaler']
                self.is_trained = True
            print(f"Model loaded from {filepath}")
        except FileNotFoundError:
            print(f"Model file not found: {filepath}")


if __name__ == "__main__":
    # Train and test the predictor
    predictor = AWGWaterProductionPredictor()
    predictor.train()
    
    # Test predictions
    print("\n" + "="*80)
    print("SEASONAL WATER PRODUCTION PREDICTIONS")
    print("="*80 + "\n")
    
    test_regions = ["dubai_uae", "delhi_india", "sydney_australia"]
    
    for region in test_regions:
        result = predictor.predict_seasonal_production(region)
        if "error" not in result:
            print(f"Region: {result['region']}")
            print(f"Annual Average: {result['annual_average_per_day']} liters/day")
            print(f"Annual Total: {result['annual_total_liters']} liters")
            print()
    
    predictor.save_model()