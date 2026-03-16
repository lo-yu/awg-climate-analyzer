# AWG Climate Suitability Analyzer

A full-stack ML-powered system that analyzes climate data and predicts whether
**Atmospheric Water Generators (AWGs)** can effectively generate water at a given location.

---

## Architecture

```
awg-climate-analyzer/
├── backend/
│   ├── main.py              # FastAPI app — all API endpoints
│   ├── weather_api.py       # OpenWeatherMap integration + mock data
│   ├── psychrometrics.py    # Saturation VP, AH, dew point calculations
│   ├── ml_model.py          # RandomForestRegressor — train, save, predict
│   ├── awg_analysis.py      # Full pipeline orchestration + scoring
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variable template
└── frontend/
    ├── public/index.html
    └── src/
        ├── App.js           # React dashboard — all UI components
        ├── App.css          # Dark industrial dashboard styles
        └── index.js         # Entry point
```

---

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# (Optional) Add your OpenWeatherMap API key
cp .env.example .env
# Edit .env and add your key — app works in demo mode without it

# Train the ML model (creates model.pkl)
python ml_model.py

# Start the API server
uvicorn main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`

API docs (Swagger UI): `http://localhost:8000/docs`

---

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start React dev server
npm start
```

The dashboard will be available at `http://localhost:3000`

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `GET /weather?city=Delhi` | GET | Fetch real-time weather data |
| `GET /awg-analysis?city=Mumbai` | GET | Psychrometric calculations + water potential |
| `GET /prediction?city=Chennai` | GET | Full ML prediction + suitability score |
| `GET /historical?city=Delhi` | GET | Monthly trend data for charts |
| `GET /health` | GET | Health check |
| `GET /docs` | GET | Interactive Swagger API docs |

**Coordinate-based queries:**
```
GET /prediction?lat=28.6139&lon=77.2090
```

---

## Features

### Weather Data (OpenWeatherMap)
- Temperature (°C), Relative Humidity (%), Pressure (hPa)
- Wind speed, Dew point, Weather description
- Falls back to realistic mock data if no API key is provided

### Psychrometric Calculations
```
Saturation Vapor Pressure:  es = 6.112 × exp((17.67 × T) / (T + 243.5))
Actual Vapor Pressure:      e  = (RH / 100) × es
Absolute Humidity:          AH = (2.1674 × e × 100) / (273.15 + T)  [g/m³]
```

### Water Extraction Model
```
Airflow: 500 m³/hour
Daily water vapor: AH × 500 × 24 hours
AWG efficiency: 40%
Extracted water: water_vapor × 0.4  [liters/day]
```

### ML Model (RandomForestRegressor)
- 1000 synthetic training samples with realistic climate ranges
- Features: temperature, humidity, dew_point, pressure, month
- Target: water_output_liters_per_day
- MAE: ~5.3 L/day
- Saved to `model.pkl` after first training run

### AWG Suitability Score (0–100)
| Component | Weight | Description |
|---|---|---|
| Humidity Factor | 40% | Optimal at 60–90% RH |
| Predicted Water Output | 30% | Normalized to 150 L/day max |
| Temperature Suitability | 30% | Optimal at 20–35°C |

### Recommendation Engine
| Output | System Recommended |
|---|---|
| < 50 L/day | Small AWG Unit |
| 50–150 L/day | Medium AWG Unit |
| > 150 L/day | Large AWG System |

---

## Example Results

| Location | Temp | RH | Predicted Output | Score | Recommendation |
|---|---|---|---|---|---|
| Delhi | 32°C | 65% | 103.7 L/day | 79.6/100 | Medium AWG Unit |
| Mumbai | 29°C | 82% | 115.6 L/day | 89.6/100 | Medium AWG Unit |
| Chennai | 31°C | 78% | 125.0 L/day | 89.7/100 | Medium AWG Unit |
| Rajasthan | 38°C | 28% | 64.6 L/day | 50.9/100 | Medium AWG Unit |
| Ladakh | 8°C | 35% | 14.4 L/day | 27.6/100 | Small AWG Unit |

---

## Dashboard Features

- **Location search** — city name or lat/lon coordinates
- **Quick presets** — Delhi, Mumbai, Rajasthan, Ladakh, Bangalore, Chennai
- **6 real-time stat cards** — temperature, humidity, pressure, AH, water vapor, extracted liters
- **Suitability score gauge** — animated SVG arc meter (0–100)
- **ML prediction panel** — daily output + recommendation + psychrometric breakdown
- **Interactive map** — Leaflet.js with CartoDB dark tiles, location marker
- **Monthly water chart** — Line chart showing annual AWG potential trend
- **Temp & humidity chart** — Dual-axis seasonal variation

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, Uvicorn |
| ML | Scikit-learn (RandomForestRegressor), Pandas, NumPy |
| Weather | OpenWeatherMap API (free tier) |
| Frontend | React 18, Chart.js 4, Leaflet.js, Axios |
| Styling | Custom CSS (Space Mono + DM Sans fonts) |

---

## OpenWeatherMap API Key (Optional)

The app runs fully in **demo mode** without an API key using realistic pre-set data for Indian cities. To enable live weather:

1. Register at https://openweathermap.org/api
2. Get your free API key (1000 calls/day free)
3. Add it to `backend/.env`:
   ```
   OPENWEATHER_API_KEY=your_key_here
   ```
4. Restart the backend server

---

## License

MIT
