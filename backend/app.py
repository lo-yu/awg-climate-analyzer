from flask import Flask, jsonify, request
from flask_cors import CORS
from data_collection import collect_all_regions_data
from awg_analyzer import AWGSuitabilityAnalyzer
from ml_predictor import AWGWaterProductionPredictor
import os

app = Flask(__name__)
CORS(app)

# Initialize analyzer and predictor
analyzer = AWGSuitabilityAnalyzer()
predictor = AWGWaterProductionPredictor()

@app.route('/')
def home():
    return "AWG Climate Suitability Analyzer Backend - Running!"

@app.route('/api/collect-data', methods=['POST'])
def collect_data():
    """Collect climate data from APIs"""
    try:
        data = collect_all_regions_data()
        return jsonify({"status": "success", "message": "Data collection complete"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/train-model', methods=['POST'])
def train_model():
    """Train ML model"""
    try:
        predictor.train()
        predictor.save_model()
        return jsonify({"status": "success", "message": "Model training complete"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/analyze', methods=['GET'])
def analyze():
    """Get suitability analysis for all regions"""
    try:
        results = analyzer.analyze_all_regions()
        return jsonify({"status": "success", "results": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/analyze/<region_code>', methods=['GET'])
def analyze_region(region_code):
    """Get analysis for specific region"""
    try:
        result = analyzer.calculate_suitability_score(region_code)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/predict/<region_code>', methods=['GET'])
def predict_production(region_code):
    """Get seasonal water production predictions"""
    try:
        result = predictor.predict_seasonal_production(region_code)
        return jsonify({"status": "success", **result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/sizing/<region_code>', methods=['GET'])
def get_sizing(region_code):
    """Get system sizing recommendation"""
    try:
        daily_need = float(request.args.get('daily_need', 100))
        result = analyzer.get_system_size_recommendation(region_code, daily_need)
        return jsonify({"status": "success", **result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Collect data on startup
    print("Collecting climate data...")
    collect_all_regions_data()
    
    # Train model
    print("Training ML model...")
    predictor.train()
    predictor.save_model()
    
    # Run Flask app
    app.run(debug=True, port=5000)