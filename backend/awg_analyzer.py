import json
import pandas as pd
from typing import Dict, List
import numpy as np

class AWGSuitabilityAnalyzer:
    """
    Analyzes climate suitability for Atmospheric Water Generation
    Based on research: AWG efficiency peaks at 40-80% relative humidity
    Temperature range: 15-40°C optimal, can work outside but less efficient
    """
    
    # AWG efficiency parameters (research-based)
    OPTIMAL_HUMIDITY_MIN = 40
    OPTIMAL_HUMIDITY_MAX = 80
    OPTIMAL_TEMP_MIN = 15
    OPTIMAL_TEMP_MAX = 40
    
    def __init__(self, climate_data_file="climate_data.json"):
        """Initialize with climate data"""
        try:
            with open(climate_data_file, 'r') as f:
                self.climate_data = json.load(f)
        except FileNotFoundError:
            self.climate_data = {}
    
    def calculate_suitability_score(self, region_code: str) -> Dict:
        """
        Calculate AWG suitability score for a region (0-100)
        Factors:
        - Humidity levels (40-80% is optimal)
        - Temperature stability
        - Seasonal variations
        - Overall water generation potential
        """
        if region_code not in self.climate_data:
            return {"error": "Region not found"}
        
        region_data = self.climate_data[region_code]
        monthly_data = region_data.get("nasa_monthly_data", [])
        
        if not monthly_data:
            return {"error": "No climate data available"}
        
        # Extract humidity and temperature data
        humidities = [d["humidity"] for d in monthly_data if d["humidity"]]
        temperatures = [d["temperature"] for d in monthly_data if d["temperature"]]
        
        if not humidities or not temperatures:
            return {"error": "Insufficient data"}
        
        # Calculate metrics
        avg_humidity = np.mean(humidities)
        min_humidity = np.min(humidities)
        max_humidity = np.max(humidities)
        humidity_std = np.std(humidities)
        
        avg_temp = np.mean(temperatures)
        min_temp = np.min(temperatures)
        max_temp = np.max(temperatures)
        
        # Score calculation (0-100)
        humidity_score = self._score_humidity(avg_humidity, min_humidity, max_humidity)
        temp_score = self._score_temperature(avg_temp, min_temp, max_temp)
        stability_score = self._score_stability(humidity_std, temperatures)
        
        # Weighted average (60% humidity, 25% temperature, 15% stability)
        overall_score = (humidity_score * 0.60 + 
                        temp_score * 0.25 + 
                        stability_score * 0.15)
        
        return {
            "region_code": region_code,
            "region_name": region_data["name"],
            "overall_suitability_score": round(overall_score, 2),
            "humidity_score": round(humidity_score, 2),
            "temperature_score": round(temp_score, 2),
            "stability_score": round(stability_score, 2),
            "avg_humidity": round(avg_humidity, 2),
            "humidity_range": f"{min_humidity:.1f}% - {max_humidity:.1f}%",
            "avg_temperature": round(avg_temp, 2),
            "temp_range": f"{min_temp:.1f}°C - {max_temp:.1f}°C",
            "monthly_data": monthly_data,
            "recommendation": self._get_recommendation(overall_score)
        }
    
    def _score_humidity(self, avg, min_val, max_val) -> float:
        """Score based on humidity levels (ideal: 40-80%)"""
        if avg < self.OPTIMAL_HUMIDITY_MIN:
            # Too dry - very low water generation
            return max(0, (avg / self.OPTIMAL_HUMIDITY_MIN) * 40)
        elif avg <= self.OPTIMAL_HUMIDITY_MAX:
            # In optimal range
            return 100
        else:
            # Too humid - potential issues with water quality/efficiency
            return max(40, 100 - (avg - self.OPTIMAL_HUMIDITY_MAX) * 2)
    
    def _score_temperature(self, avg, min_val, max_val) -> float:
        """Score based on temperature (ideal: 15-40°C)"""
        if avg < self.OPTIMAL_TEMP_MIN:
            return (avg + 10) * 5  # Cold regions still viable
        elif avg <= self.OPTIMAL_TEMP_MAX:
            return 100
        else:
            # Hot regions still good
            return max(70, 100 - (avg - self.OPTIMAL_TEMP_MAX))
    
    def _score_stability(self, humidity_std, temperatures) -> float:
        """Score based on climate stability (lower std = more stable = better)"""
        temp_std = np.std(temperatures)
        
        # Stability score (lower variance is better)
        if humidity_std < 10:
            stability = 100
        elif humidity_std < 20:
            stability = 80
        elif humidity_std < 30:
            stability = 60
        else:
            stability = max(30, 100 - humidity_std * 2)
        
        return stability
    
    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on suitability score"""
        if score >= 80:
            return "Excellent - Highly suitable for AWG deployment"
        elif score >= 60:
            return "Good - Suitable for AWG with proper design"
        elif score >= 40:
            return "Moderate - Viable but requires optimization"
        elif score >= 20:
            return "Poor - Limited viability, consider hybrid systems"
        else:
            return "Not recommended - Very low water generation potential"
    
    def analyze_all_regions(self) -> List[Dict]:
        """Analyze and rank all regions"""
        results = []
        
        for region_code in self.climate_data.keys():
            analysis = self.calculate_suitability_score(region_code)
            if "error" not in analysis:
                results.append(analysis)
        
        # Sort by overall suitability score (descending)
        results.sort(key=lambda x: x["overall_suitability_score"], reverse=True)
        return results
    
    def get_system_size_recommendation(self, region_code: str, daily_water_need: float = 100) -> Dict:
        """
        Recommend AWG system size based on climate data
        daily_water_need: liters per day needed
        Modern AWG systems produce 5-15 liters/day depending on conditions
        """
        analysis = self.calculate_suitability_score(region_code)
        
        if "error" in analysis:
            return analysis
        
        score = analysis["overall_suitability_score"]
        
        # Estimate water production efficiency
        if score >= 80:
            avg_production = 12  # liters/day per unit
            efficiency = "High"
        elif score >= 60:
            avg_production = 8
            efficiency = "Good"
        elif score >= 40:
            avg_production = 5
            efficiency = "Moderate"
        else:
            avg_production = 2
            efficiency = "Low"
        
        systems_needed = max(1, round(daily_water_need / avg_production, 1))
        
        return {
            "region": analysis["region_name"],
            "daily_water_needed": daily_water_need,
            "estimated_production_per_unit": avg_production,
            "production_efficiency": efficiency,
            "systems_recommended": systems_needed,
            "total_estimated_production": round(avg_production * systems_needed, 1),
            "note": f"Estimates based on suitability score of {score}/100"
        }


if __name__ == "__main__":
    analyzer = AWGSuitabilityAnalyzer()
    
    # Analyze all regions
    results = analyzer.analyze_all_regions()
    
    print("\n" + "="*80)
    print("AWG CLIMATE SUITABILITY ANALYSIS - ALL REGIONS RANKED")
    print("="*80 + "\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['region_name']}")
        print(f"   Overall Score: {result['overall_suitability_score']}/100")
        print(f"   Avg Humidity: {result['avg_humidity']}% ({result['humidity_range']})")
        print(f"   Avg Temp: {result['avg_temperature']}°C ({result['temp_range']})")
        print(f"   Recommendation: {result['recommendation']}")
        print()