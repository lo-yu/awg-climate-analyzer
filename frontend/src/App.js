import React, { useState, useEffect, useCallback } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend, ArcElement, RadialLinearScale, Filler } from 'chart.js';
import { Bar, Line, Doughnut } from 'react-chartjs-2';
import axios from 'axios';
import './App.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend, ArcElement, RadialLinearScale, Filler);

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const PRESET_LOCATIONS = [
  { label: 'Delhi', city: 'delhi', lat: 28.6139, lon: 77.2090 },
  { label: 'Mumbai', city: 'mumbai', lat: 19.0760, lon: 72.8777 },
  { label: 'Rajasthan', city: 'rajasthan', lat: 27.0238, lon: 74.2179 },
  { label: 'Ladakh', city: 'ladakh', lat: 34.1526, lon: 77.5770 },
  { label: 'Bangalore', city: 'bangalore', lat: 12.9716, lon: 77.5946 },
  { label: 'Chennai', city: 'chennai', lat: 13.0827, lon: 80.2707 },
];

function ScoreMeter({ score }) {
  const clamp = Math.min(100, Math.max(0, score));
  const angle = (clamp / 100) * 180 - 90;
  const color = clamp >= 70 ? '#22c55e' : clamp >= 45 ? '#f59e0b' : clamp >= 25 ? '#f97316' : '#ef4444';

  return (
    <div className="score-meter">
      <svg viewBox="0 0 200 110" className="meter-svg">
        <path d="M 10 100 A 90 90 0 0 1 190 100" fill="none" stroke="#1e293b" strokeWidth="16" strokeLinecap="round" />
        <path
          d="M 10 100 A 90 90 0 0 1 190 100"
          fill="none"
          stroke={color}
          strokeWidth="16"
          strokeLinecap="round"
          strokeDasharray={`${(clamp / 100) * 283} 283`}
        />
        <g transform={`rotate(${angle}, 100, 100)`}>
          <line x1="100" y1="100" x2="100" y2="20" stroke="#f8fafc" strokeWidth="3" strokeLinecap="round" />
          <circle cx="100" cy="100" r="6" fill="#f8fafc" />
        </g>
        <text x="100" y="95" textAnchor="middle" fill={color} fontSize="28" fontFamily="Space Mono" fontWeight="700">{clamp}</text>
        <text x="100" y="108" textAnchor="middle" fill="#64748b" fontSize="9" fontFamily="DM Sans">/100</text>
      </svg>
    </div>
  );
}

function WeatherIcon({ icon }) {
  const iconUrl = icon ? `https://openweathermap.org/img/wn/${icon}@2x.png` : null;
  return iconUrl ? <img src={iconUrl} alt="weather" className="weather-icon-img" /> : <span className="weather-icon-fallback">☁</span>;
}

function StatCard({ label, value, unit, sub, accent }) {
  return (
    <div className="stat-card" style={{ '--accent': accent || 'var(--teal)' }}>
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}<span className="stat-unit">{unit}</span></div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  );
}

function MapView({ lat, lon, city }) {
  useEffect(() => {
    if (!lat || !lon) return;

    // Dynamically load Leaflet
    const existingMap = document.getElementById('map-instance');
    if (existingMap) existingMap.innerHTML = '';

    setTimeout(() => {
      try {
        const L = window.L;
        if (!L) return;

        const map = L.map('map-instance').setView([lat, lon], 8);

        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
          attribution: '© CartoDB',
          maxZoom: 19,
        }).addTo(map);

        const marker = L.circleMarker([lat, lon], {
          radius: 10,
          fillColor: '#06b6d4',
          color: '#fff',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.9,
        }).addTo(map);

        marker.bindPopup(`<b>${city}</b><br/>Lat: ${lat.toFixed(4)}, Lon: ${lon.toFixed(4)}`).openPopup();
      } catch (e) {
        console.error('Map error:', e);
      }
    }, 200);
  }, [lat, lon, city]);

  return <div id="map-instance" className="map-container" />;
}

export default function App() {
  const [cityInput, setCityInput] = useState('');
  const [latInput, setLatInput] = useState('');
  const [lonInput, setLonInput] = useState('');
  const [inputMode, setInputMode] = useState('city');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [data, setData] = useState(null);
  const [historical, setHistorical] = useState(null);
  const [activeCity, setActiveCity] = useState('');

  const fetchAnalysis = useCallback(async (params) => {
    setLoading(true);
    setError('');
    try {
      const resp = await axios.get(`${API_BASE}/prediction`, { params });
      setData(resp.data);

      const cityName = resp.data?.location?.city || params.city || 'delhi';
      setActiveCity(cityName);

      const hist = await axios.get(`${API_BASE}/historical`, { params: { city: cityName } });
      setHistorical(hist.data);
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to fetch data. Is the backend running?');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputMode === 'city' && cityInput.trim()) {
      fetchAnalysis({ city: cityInput.trim() });
    } else if (inputMode === 'coords' && latInput && lonInput) {
      fetchAnalysis({ lat: parseFloat(latInput), lon: parseFloat(lonInput) });
    }
  };

  const handlePreset = (preset) => {
    setCityInput(preset.city);
    setInputMode('city');
    fetchAnalysis({ city: preset.city });
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#94a3b8', font: { family: 'DM Sans', size: 11 } } },
      tooltip: { backgroundColor: '#0f172a', borderColor: '#334155', borderWidth: 1 },
    },
    scales: {
      x: { ticks: { color: '#64748b', font: { family: 'Space Mono', size: 10 } }, grid: { color: '#1e293b' } },
      y: { ticks: { color: '#64748b', font: { family: 'Space Mono', size: 10 } }, grid: { color: '#1e293b' } },
    },
  };

  const monthLabels = historical?.monthly_data?.map(d => d.month) || [];

  const waterChartData = {
    labels: monthLabels,
    datasets: [{
      label: 'Predicted Water (L/day)',
      data: historical?.monthly_data?.map(d => d.predicted_water_liters) || [],
      backgroundColor: 'rgba(6,182,212,0.25)',
      borderColor: '#06b6d4',
      borderWidth: 2,
      fill: true,
      tension: 0.4,
      pointBackgroundColor: '#06b6d4',
      pointRadius: 4,
    }],
  };

  const tempHumidChartData = {
    labels: monthLabels,
    datasets: [
      {
        label: 'Avg Temp (°C)',
        data: historical?.monthly_data?.map(d => d.avg_temperature_c) || [],
        backgroundColor: 'rgba(239,68,68,0.2)',
        borderColor: '#ef4444',
        borderWidth: 2,
        yAxisID: 'y',
        tension: 0.4,
        fill: false,
        pointBackgroundColor: '#ef4444',
        pointRadius: 3,
      },
      {
        label: 'Avg Humidity (%)',
        data: historical?.monthly_data?.map(d => d.avg_humidity_pct) || [],
        backgroundColor: 'rgba(34,197,94,0.2)',
        borderColor: '#22c55e',
        borderWidth: 2,
        yAxisID: 'y1',
        tension: 0.4,
        fill: false,
        pointBackgroundColor: '#22c55e',
        pointRadius: 3,
      },
    ],
  };

  const tempHumidOptions = {
    ...chartOptions,
    scales: {
      ...chartOptions.scales,
      y: { ...chartOptions.scales.y, position: 'left', title: { display: true, text: 'Temp °C', color: '#ef4444' } },
      y1: { ...chartOptions.scales.y, position: 'right', title: { display: true, text: 'Humidity %', color: '#22c55e' }, grid: { drawOnChartArea: false } },
    },
  };

  const score = data?.suitability?.total_score || 0;
  const suitability = data?.suitability || {};
  const weather = data?.weather || {};
  const psychro = data?.psychrometrics || {};
  const extraction = data?.water_extraction || {};
  const ml = data?.ml_prediction || {};
  const loc = data?.location || {};

  const scoreData = {
    datasets: [{
      data: [score, 100 - score],
      backgroundColor: [
        score >= 70 ? '#22c55e' : score >= 45 ? '#f59e0b' : score >= 25 ? '#f97316' : '#ef4444',
        '#1e293b',
      ],
      borderWidth: 0,
      cutout: '78%',
    }],
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo-area">
            <div className="logo-icon">
              <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="20" cy="20" r="18" stroke="#06b6d4" strokeWidth="1.5" />
                <path d="M20 8 C14 14 10 17 10 22 C10 27.5 14.5 32 20 32 C25.5 32 30 27.5 30 22 C30 17 26 14 20 8Z" fill="#06b6d4" opacity="0.8" />
                <circle cx="20" cy="22" r="5" fill="#0f172a" />
                <circle cx="20" cy="22" r="2" fill="#06b6d4" />
              </svg>
            </div>
            <div>
              <h1 className="app-title">AWG CLIMATE ANALYZER</h1>
              <p className="app-subtitle">Atmospheric Water Generator Suitability Intelligence</p>
            </div>
          </div>
          <div className="header-badge">
            <span className="badge-dot" />
            ML-POWERED
          </div>
        </div>
      </header>

      <main className="app-main">
        {/* Search Panel */}
        <section className="search-section">
          <div className="input-mode-toggle">
            <button className={`mode-btn ${inputMode === 'city' ? 'active' : ''}`} onClick={() => setInputMode('city')}>
              CITY NAME
            </button>
            <button className={`mode-btn ${inputMode === 'coords' ? 'active' : ''}`} onClick={() => setInputMode('coords')}>
              COORDINATES
            </button>
          </div>

          <form onSubmit={handleSubmit} className="search-form">
            {inputMode === 'city' ? (
              <input
                className="search-input"
                type="text"
                placeholder="Enter city name... (e.g. Delhi, Mumbai)"
                value={cityInput}
                onChange={e => setCityInput(e.target.value)}
              />
            ) : (
              <div className="coord-inputs">
                <input className="search-input half" type="number" placeholder="Latitude" value={latInput} onChange={e => setLatInput(e.target.value)} step="any" />
                <input className="search-input half" type="number" placeholder="Longitude" value={lonInput} onChange={e => setLonInput(e.target.value)} step="any" />
              </div>
            )}
            <button className="analyze-btn" type="submit" disabled={loading}>
              {loading ? <span className="spinner" /> : null}
              {loading ? 'ANALYZING...' : 'ANALYZE LOCATION'}
            </button>
          </form>

          <div className="preset-chips">
            {PRESET_LOCATIONS.map(p => (
              <button key={p.city} className={`preset-chip ${activeCity.toLowerCase() === p.city ? 'active' : ''}`} onClick={() => handlePreset(p)}>
                {p.label}
              </button>
            ))}
          </div>

          {error && <div className="error-banner">{error}</div>}
        </section>

        {data && (
          <>
            {/* Location Overview */}
            <section className="location-banner">
              <div className="location-info">
                <WeatherIcon icon={weather.weather_icon} />
                <div>
                  <h2 className="location-name">{loc.city}{loc.country ? `, ${loc.country}` : ''}</h2>
                  <p className="location-coords">
                    {loc.latitude?.toFixed(4)}°N · {loc.longitude?.toFixed(4)}°E · {weather.weather_description}
                  </p>
                  {data.is_mock && <span className="mock-badge">DEMO DATA — Add OpenWeatherMap API key for live data</span>}
                </div>
              </div>
              <div className="feasibility-badge" style={{ background: suitability.feasibility_color + '22', borderColor: suitability.feasibility_color, color: suitability.feasibility_color }}>
                {suitability.feasibility}
              </div>
            </section>

            {/* Main Stats Grid */}
            <div className="stats-grid">
              <StatCard label="TEMPERATURE" value={weather.temperature_c} unit="°C" sub={`Feels like ${weather.feels_like_c}°C`} accent="#ef4444" />
              <StatCard label="HUMIDITY" value={weather.relative_humidity_pct} unit="%" sub={`Dew pt: ${weather.dew_point_c}°C`} accent="#22c55e" />
              <StatCard label="PRESSURE" value={weather.pressure_hpa} unit=" hPa" sub={`Wind: ${weather.wind_speed_ms} m/s`} accent="#a78bfa" />
              <StatCard label="ABS. HUMIDITY" value={psychro.absolute_humidity_g_m3} unit=" g/m³" sub="Moisture content" accent="#06b6d4" />
              <StatCard label="WATER VAPOR" value={(extraction.water_vapor_grams_per_hour / 1000).toFixed(2)} unit=" L/hr" sub="At 500m³/hr airflow" accent="#f59e0b" />
              <StatCard label="EXTRACTED" value={extraction.extracted_liters_per_hour} unit=" L/hr" sub="At 40% efficiency" accent="#06b6d4" />
            </div>

            {/* Score + Prediction + Map Row */}
            <div className="analysis-grid">
              {/* Suitability Score */}
              <div className="card score-card">
                <h3 className="card-title">AWG SUITABILITY SCORE</h3>
                <ScoreMeter score={score} />
                <div className="score-breakdown">
                  <div className="score-row">
                    <span>Humidity Factor (40%)</span>
                    <span style={{ color: '#22c55e' }}>{suitability.humidity_score}</span>
                  </div>
                  <div className="score-row">
                    <span>Water Output (30%)</span>
                    <span style={{ color: '#06b6d4' }}>{suitability.water_score}</span>
                  </div>
                  <div className="score-row">
                    <span>Temperature (30%)</span>
                    <span style={{ color: '#ef4444' }}>{suitability.temperature_score}</span>
                  </div>
                </div>
              </div>

              {/* ML Prediction */}
              <div className="card prediction-card">
                <h3 className="card-title">ML PREDICTION</h3>
                <div className="prediction-value">
                  <span className="pred-num">{ml.predicted_water_output_liters_per_day}</span>
                  <span className="pred-unit">L/day</span>
                </div>
                <div className="recommendation-box">
                  <div className="rec-icon">💧</div>
                  <div>
                    <div className="rec-title">{suitability.recommendation}</div>
                    <div className="rec-detail">{suitability.recommendation_detail}</div>
                  </div>
                </div>
                <div className="model-info">
                  <span className="model-badge">RandomForestRegressor · 100 trees</span>
                </div>
                <div className="psychro-details">
                  <div className="psychro-row">
                    <span>Saturation VP</span><span>{psychro.saturation_vapor_pressure_hpa} hPa</span>
                  </div>
                  <div className="psychro-row">
                    <span>Actual VP</span><span>{psychro.actual_vapor_pressure_hpa} hPa</span>
                  </div>
                  <div className="psychro-row">
                    <span>Daily Physics Est.</span><span>{extraction.extracted_liters_per_day_physics} L</span>
                  </div>
                </div>
              </div>

              {/* Map */}
              <div className="card map-card">
                <h3 className="card-title">LOCATION MAP</h3>
                <MapView lat={loc.latitude} lon={loc.longitude} city={loc.city} />
                <div className="map-coords">
                  {loc.latitude?.toFixed(6)}°N, {loc.longitude?.toFixed(6)}°E
                </div>
              </div>
            </div>

            {/* Charts */}
            {historical && (
              <div className="charts-grid">
                <div className="card chart-card">
                  <h3 className="card-title">MONTHLY WATER GENERATION POTENTIAL</h3>
                  <div className="chart-wrap">
                    <Line data={waterChartData} options={chartOptions} />
                  </div>
                </div>
                <div className="card chart-card">
                  <h3 className="card-title">TEMPERATURE & HUMIDITY TRENDS</h3>
                  <div className="chart-wrap">
                    <Line data={tempHumidChartData} options={tempHumidOptions} />
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {!data && !loading && (
          <div className="empty-state">
            <div className="empty-icon">
              <svg viewBox="0 0 80 80" fill="none">
                <circle cx="40" cy="40" r="38" stroke="#1e293b" strokeWidth="2" />
                <path d="M40 15 C28 27 20 32 20 43 C20 55 29 65 40 65 C51 65 60 55 60 43 C60 32 52 27 40 15Z" fill="#0f172a" stroke="#06b6d4" strokeWidth="1.5" />
                <circle cx="40" cy="43" r="10" fill="#0f172a" stroke="#06b6d4" strokeWidth="1.5" />
                <circle cx="40" cy="43" r="4" fill="#06b6d4" opacity="0.6" />
              </svg>
            </div>
            <h2 className="empty-title">Select a Location to Analyze</h2>
            <p className="empty-sub">Enter a city name, coordinates, or pick a preset to evaluate AWG potential.</p>
            <div className="empty-chips">
              {PRESET_LOCATIONS.map(p => (
                <button key={p.city} className="preset-chip" onClick={() => handlePreset(p)}>{p.label}</button>
              ))}
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <span>AWG CLIMATE ANALYZER · RandomForest ML · Psychrometric Calculations · OpenWeatherMap</span>
      </footer>
    </div>
  );
}
