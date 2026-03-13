# AWG Climate Suitability Analyzer

An intelligent web application that analyzes global atmospheric water generation (AWG) potential based on climate data and machine learning predictions.

## 🌟 Features

### Phase 1 - MVP ✅
- **Climate Data Collection** - Fetches real weather data from NASA POWER and OpenWeatherMap APIs
- **Suitability Scoring** - Analyzes 10 global regions for AWG viability (0-100 score)
- **Interactive Rankings** - View regions ranked by suitability with search functionality
- **Visual Dashboard** - Stats overview with interactive map using Leaflet.js

### Phase 2 - ML Enhanced ✅
- **Water Production Predictions** - ML model predicts monthly water generation potential
- **Seasonal Forecasting** - Visualize predicted water output throughout the year
- **System Sizing Calculator** - Recommends AWG system size based on water needs
- **Chart Visualizations** - Interactive charts showing production trends

## 🛠️ Technology Stack

**Backend:**
- Flask (Python web framework)
- scikit-learn (Machine Learning)
- pandas (Data analysis)
- requests (API calls)

**Frontend:**
- HTML5, CSS3, Vanilla JavaScript
- Chart.js (Data visualization)
- Leaflet.js (Interactive maps)

**Data Sources:**
- NASA POWER API (historical climate data - free)
- OpenWeatherMap (current weather - free tier)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Backend Setup

1. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Run the backend**
```bash
python app.py
```

The backend will:
- Collect climate data from APIs
- Train the ML model
- Start the Flask server on `http://localhost:5000`

### Frontend Setup

1. **Open the application**
```bash
cd frontend
python -m http.server 8000
```

Then visit `http://localhost:8000`

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analyze` | GET | Get suitability scores for all regions |
| `/api/analyze/<region_code>` | GET | Get detailed analysis for a specific region |
| `/api/predict/<region_code>` | GET | Get seasonal water production predictions |
| `/api/sizing/<region_code>` | GET | Get system sizing recommendation |
| `/api/health` | GET | Health check |

## 📊 Project Structure

```
awg-climate-analyzer/
├── backend/
│   ├── app.py                    # Flask server
│   ├── data_collection.py        # NASA API integration
│   ├── awg_analyzer.py           # Suitability algorithm
│   ├── ml_predictor.py           # ML model
│   ├── requirements.txt          # Python packages
│   └── climate_data.json         # Generated data
├── frontend/
│   ├── index.html                # Main page
│   ├── styles.css                # Styles
│   └── app.js                    # Frontend logic
├── README.md                      # Project info
└── .gitignore                     # Git ignore rules
```

## 🔍 How It Works

### Phase 1: Climate Analysis
1. **Data Collection**: Fetches real climate data for 10 global regions
2. **Suitability Scoring**: Analyzes humidity, temperature, and stability
3. **Ranking**: Regions ranked by AWG viability (0-100 scale)
4. **Visualization**: Interactive map and rankings dashboard

### Phase 2: ML Predictions
1. **Model Training**: Trains Random Forest on climate patterns
2. **Seasonal Forecasting**: Predicts water production for each month
3. **System Sizing**: Recommends AWG capacity based on water needs
4. **Performance Insights**: Charts and statistics for decision making

## 📈 Suitability Scoring

Scoring is based on three factors:

| Factor | Weight | Optimal Range |
|--------|--------|----------------|
| Humidity | 60% | 40-80% |
| Temperature | 25% | 15-40°C |
| Stability | 15% | Low variance |

**Score Interpretation:**
- **80-100**: Excellent - Highly suitable
- **60-79**: Good - Suitable with proper design
- **40-59**: Moderate - Viable with optimization
- **20-39**: Poor - Limited viability
- **0-19**: Not recommended

## 🔧 Customization

### Add More Regions
Edit `backend/data_collection.py`:
```python
REGIONS = [
    {"name": "Your City", "lat": 0.0, "lon": 0.0, "region_code": "your_city"},
    # Add more...
]
```

### Change AWG Parameters
Modify thresholds in `awg_analyzer.py`:
```python
OPTIMAL_HUMIDITY_MIN = 40
OPTIMAL_HUMIDITY_MAX = 80
OPTIMAL_TEMP_MIN = 15
OPTIMAL_TEMP_MAX = 40
```

## 📚 Future Enhancements

- [ ] Real-time weather updates
- [ ] Cost-benefit analysis with ROI calculator
- [ ] Integration with actual AWG manufacturer data
- [ ] User accounts and saved analyses
- [ ] Mobile app
- [ ] API for third-party developers
- [ ] Advanced ML models (neural networks, LSTM)
- [ ] Optimization for specific AWG technologies

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Built with ❤️ for sustainable water solutions**