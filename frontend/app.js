let analysisData = [];
let predictionChart = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadAnalysisData();
});

function showTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from all buttons
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

async function loadAnalysisData() {
    try {
        // Fetch analysis results from backend
        const response = await fetch('http://localhost:5000/api/analyze');
        const data = await response.json();
        analysisData = data.results;
        
        updateOverview();
        updateRankings();
        populateSelects();
        initMap();
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('rankingsList').innerHTML = '<p>Error loading data. Make sure backend is running on http://localhost:5000</p>';
    }
}

function updateOverview() {
    if (analysisData.length === 0) return;
    
    document.getElementById('regionCount').textContent = analysisData.length;
    
    const topRegion = analysisData[0];
    document.getElementById('bestRegion').textContent = topRegion.region_name;
    document.getElementById('topScore').textContent = topRegion.overall_suitability_score;
    
    const avgScore = (analysisData.reduce((sum, r) => sum + r.overall_suitability_score, 0) / analysisData.length).toFixed(1);
    document.getElementById('avgScore').textContent = avgScore;
}

function updateRankings() {
    const rankingsList = document.getElementById('rankingsList');
    rankingsList.innerHTML = '';
    
    analysisData.forEach((region, index) => {
        const item = document.createElement('div');
        item.className = 'ranking-item';
        item.onclick = () => showRegionDetails(region);
        
        const scoreColor = region.overall_suitability_score >= 80 ? '#4caf50' :
                          region.overall_suitability_score >= 60 ? '#2196f3' :
                          region.overall_suitability_score >= 40 ? '#ff9800' : '#f44336';
        
        item.innerHTML = `
            <div class="ranking-number">#${index + 1}</div>
            <div class="ranking-info">
                <div class="ranking-name">${region.region_name}</div>
                <div class="ranking-details">
                    Humidity: ${region.avg_humidity}% | Temp: ${region.avg_temperature}°C
                </div>
                <div class="ranking-details">
                    ${region.recommendation}
                </div>
            </div>
            <div class="ranking-score" style="background: ${scoreColor};">
                ${region.overall_suitability_score}
            </div>
        `;
        
        rankingsList.appendChild(item);
    });
}

function filterRegions() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const items = document.querySelectorAll('.ranking-item');
    
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.classList.toggle('hidden', !text.includes(searchTerm));
    });
}

function populateSelects() {
    const regionSelect = document.getElementById('regionSelect');
    const sizingSelect = document.getElementById('sizingRegion');
    
    analysisData.forEach(region => {
        const option1 = document.createElement('option');
        option1.value = region.region_code;
        option1.textContent = region.region_name;
        regionSelect.appendChild(option1);
        
        const option2 = document.createElement('option');
        option2.value = region.region_code;
        option2.textContent = region.region_name;
        sizingSelect.appendChild(option2);
    });
}

async function updatePredictionChart() {
    const regionCode = document.getElementById('regionSelect').value;
    if (!regionCode) return;
    
    try {
        const response = await fetch(`http://localhost:5000/api/predict/${regionCode}`);
        const data = await response.json();
        
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const predictions = data.monthly_predictions;
        const productionValues = predictions.map(p => p.predicted_production_liters_per_day);
        
        const ctx = document.getElementById('predictionChart').getContext('2d');
        
        if (predictionChart) {
            predictionChart.destroy();
        }
        
        predictionChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: months.slice(0, predictions.length),
                datasets: [{
                    label: 'Estimated Water Production (L/day)',
                    data: productionValues,
                    backgroundColor: 'rgba(102, 126, 234, 0.6)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Liters per Day'
                        }
                    }
                }
            }
        });
        
        // Update stats
        const statsDiv = document.getElementById('predictionStats');
        statsDiv.innerHTML = `
            <h3>Annual Production Statistics</h3>
            <div class="result-item">
                <span class="result-label">Annual Average:</span>
                <span class="result-value">${data.annual_average_per_day} L/day</span>
            </div>
            <div class="result-item">
                <span class="result-label">Annual Total:</span>
                <span class="result-value">${data.annual_total_liters} L/year</span>
            </div>
        `;
    } catch (error) {
        console.error('Error fetching predictions:', error);
    }
}

async function calculateSizing() {
    const regionCode = document.getElementById('sizingRegion').value;
    const waterNeed = parseFloat(document.getElementById('waterNeed').value) || 100;
    
    if (!regionCode) {
        alert('Please select a region');
        return;
    }
    
    try {
        const response = await fetch(`http://localhost:5000/api/sizing/${regionCode}?daily_need=${waterNeed}`);
        const data = await response.json();
        
        const resultsDiv = document.getElementById('sizingResults');
        resultsDiv.innerHTML = `
            <h3>System Sizing Recommendation</h3>
            <div class="result-item">
                <span class="result-label">Region:</span>
                <span class="result-value">${data.region}</span>
            </div>
            <div class="result-item">
                <span class="result-label">Daily Water Need:</span>
                <span class="result-value">${data.daily_water_needed} L</span>
            </div>
            <div class="result-item">
                <span class="result-label">Production per Unit:</span>
                <span class="result-value">${data.estimated_production_per_unit} L/day</span>
            </div>
            <div class="result-item">
                <span class="result-label">Efficiency:</span>
                <span class="result-value">${data.production_efficiency}</span>
            </div>
            <div class="result-item">
                <span class="result-label">Systems Recommended:</span>
                <span class="result-value">${data.systems_recommended}</span>
            </div>
            <div class="result-item">
                <span class="result-label">Total Estimated Production:</span>
                <span class="result-value">${data.total_estimated_production} L/day</span>
            </div>
        `;
    } catch (error) {
        console.error('Error calculating sizing:', error);
    }
}

function initMap() {
    // Initialize Leaflet map with marker for each region
    const map = L.map('map').setView([20, 0], 2);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    analysisData.forEach(region => {
        const color = region.overall_suitability_score >= 80 ? '#4caf50' :
                      region.overall_suitability_score >= 60 ? '#2196f3' :
                      region.overall_suitability_score >= 40 ? '#ff9800' : '#f44336';
        
        L.circleMarker([region.latitude, region.longitude], {
            radius: 8,
            fillColor: color,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).bindPopup(`
            <b>${region.region_name}</b><br>
            Score: ${region.overall_suitability_score}/100<br>
            Humidity: ${region.avg_humidity}%<br>
            Temp: ${region.avg_temperature}°C
        `).addTo(map);
    });
}

function showRegionDetails(region) {
    alert(`${region.region_name}\nScore: ${region.overall_suitability_score}/100\nHumidity: ${region.avg_humidity}%\nTemp: ${region.avg_temperature}°C\n\n${region.recommendation}`);
}