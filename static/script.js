let marketChart = null;
let autoRefreshInterval = null;
let autoRefreshEnabled = false;
let currentChartData = null;
let currentChartType = 'price';

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Analyze button
    document.getElementById('analyze-btn').addEventListener('click', () => analyzeMarket());

    // Export button
    document.getElementById('export-btn').addEventListener('click', () => showExportMenu());

    // Auto-refresh toggle
    document.getElementById('auto-refresh-toggle').addEventListener('click', toggleAutoRefresh);

    // Theme toggle
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

    // Tab navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    // Portfolio management
    document.getElementById('add-to-portfolio').addEventListener('click', addToPortfolio);

    // Alert management
    document.getElementById('add-alert').addEventListener('click', createAlert);

    // Predictor
    document.getElementById('predict-btn').addEventListener('click', generatePrediction);

    // Screener
    document.getElementById('screen-btn').addEventListener('click', runScreener);

    // Chart type selector
    document.getElementById('chart-type-select').addEventListener('change', (e) => {
        currentChartType = e.target.value;
        if (currentChartData) renderChart(currentChartData, currentChartType);
    });

    // Initialize
    initChart();
    updateMarketTicker();
    loadPortfolio();
    loadAlerts();
    loadHistory();

    // Refresh indices every 60 seconds
    setInterval(updateMarketTicker, 60000);

    // 3D Tilt Effect
    addTiltEffect();
}

function addTiltEffect() {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -5;
            const rotateY = ((x - centerX) / centerX) * 5;
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
        });
    });
}

// ============ TAB MANAGEMENT ============
function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `tab-${tabName}`);
    });
    if (tabName === 'portfolio') loadPortfolio();
    if (tabName === 'alerts') loadAlerts();
    if (tabName === 'history') loadHistory();
}

// ============ AUTO-REFRESH ============
function toggleAutoRefresh() {
    autoRefreshEnabled = !autoRefreshEnabled;
    const btn = document.getElementById('auto-refresh-toggle');
    const icon = document.getElementById('refresh-icon');

    if (autoRefreshEnabled) {
        icon.textContent = '▶️';
        btn.title = 'Auto Refresh: ON';
        btn.style.background = 'rgba(16, 185, 129, 0.2)';
        autoRefreshInterval = setInterval(() => {
            if (document.querySelector('#tab-analysis').classList.contains('active')) {
                analyzeMarket();
            }
        }, 30000);
        showNotification('Auto-refresh enabled (30s interval)', 'success');
    } else {
        icon.textContent = '⏸️';
        btn.title = 'Auto Refresh: OFF';
        btn.style.background = '';
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
            autoRefreshInterval = null;
        }
        showNotification('Auto-refresh disabled', 'info');
    }
}

// ============ THEME TOGGLE ============
function toggleTheme() {
    const body = document.body;
    const themeBtn = document.getElementById('theme-toggle');

    if (body.classList.contains('light-theme')) {
        body.classList.remove('light-theme');
        themeBtn.textContent = '🌙';
        localStorage.setItem('theme', 'dark');
    } else {
        body.classList.add('light-theme');
        themeBtn.textContent = '☀️';
        localStorage.setItem('theme', 'light');
    }
}

if (localStorage.getItem('theme') === 'light') {
    document.body.classList.add('light-theme');
    document.getElementById('theme-toggle').textContent = '☀️';
}

// ============ MARKET ANALYSIS ============
async function analyzeMarket() {
    setLoading(true);
    const symbol = document.getElementById('stock-select').value;

    try {
        const response = await fetch(`/api/analyze?symbol=${symbol}`);
        const data = await response.json();

        if (response.ok) {
            updateDashboard(data);
            if (data.triggered_alerts && data.triggered_alerts.length > 0) {
                data.triggered_alerts.forEach(alert => {
                    showNotification(`🔔 Alert: ${alert.symbol} is ${alert.type} ₹${alert.price}`, 'warning');
                });
            }
            loadHistory();
        } else {
            showNotification('Error: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        showNotification('Network Error: ' + error.message, 'error');
    } finally {
        setLoading(false);
    }
}

async function updateMarketTicker() {
    const tickerEl = document.getElementById('market-ticker');
    try {
        const response = await fetch('/api/indices');
        const data = await response.json();

        if (data.error) {
            tickerEl.innerHTML = '<span class="ticker-item" style="color: var(--danger)">Failed to load indices</span>';
            return;
        }

        tickerEl.innerHTML = '';
        for (const [name, info] of Object.entries(data)) {
            if (!info) continue;
            const changeClass = info.change >= 0 ? 'change-positive' : 'change-negative';
            const sign = info.change >= 0 ? '+' : '';
            const item = document.createElement('div');
            item.className = 'ticker-item';
            item.innerHTML = `
                <span class="ticker-name">${name}</span>
                <span class="ticker-price">₹${info.price.toFixed(2)}</span>
                <span class="ticker-change ${changeClass}">
                    ${sign}${info.change.toFixed(2)} (${sign}${info.percent_change.toFixed(2)}%)
                </span>
            `;
            tickerEl.appendChild(item);
        }
    } catch (e) {
        tickerEl.innerHTML = '<span class="ticker-item" style="color: var(--danger)">Network Error</span>';
    }
}

function setLoading(isLoading) {
    const btn = document.getElementById('analyze-btn');
    const status = document.getElementById('status-badge');

    if (isLoading) {
        btn.disabled = true;
        btn.querySelector('.btn-text').textContent = 'Analyzing...';
        status.textContent = 'Processing Data';
        status.style.color = '#f59e0b';
        status.style.background = 'rgba(245, 158, 11, 0.1)';
    } else {
        btn.disabled = false;
        btn.querySelector('.btn-text').textContent = 'Analyze Market';
        status.textContent = 'System Ready';
        status.style.color = '#10b981';
        status.style.background = 'rgba(16, 185, 129, 0.1)';
    }
}

function updateDashboard(data) {
    // Price
    document.getElementById('current-price').textContent = data.current_price.toFixed(2);

    // Signal
    const action = data.signal.action.toUpperCase();
    const signalBadge = document.getElementById('signal-action');
    signalBadge.textContent = action;
    signalBadge.className = 'signal-badge';
    if (action === 'BUY') signalBadge.classList.add('signal-buy');
    else if (action === 'SELL') signalBadge.classList.add('signal-sell');
    else signalBadge.classList.add('signal-hold');

    // Confidence
    const confidence = data.signal.confidence * 100;
    document.getElementById('confidence-fill').style.width = `${confidence}%`;
    document.getElementById('confidence-value').textContent = `${confidence.toFixed(0)}%`;

    // Reasoning
    const reasoningEl = document.getElementById('ai-reasoning');
    reasoningEl.textContent = '';
    typeWriter(data.signal.reasoning, reasoningEl);

    // Update Indicators Dashboard
    if (data.indicators) {
        updateIndicators(data.indicators);
    }

    // Chart
    currentChartData = data.market_data;
    renderChart(data.market_data, currentChartType);
}

function updateIndicators(ind) {
    const setVal = (id, val, prefix = '', suffix = '') => {
        const el = document.getElementById(id);
        if (el) el.textContent = val !== null && val !== undefined ? prefix + val + suffix : '--';
    };

    setVal('ind-rsi', ind.rsi);
    setVal('ind-macd', ind.macd);
    setVal('ind-atr', ind.atr, '₹');
    setVal('ind-adx', ind.adx);
    setVal('ind-vwap', ind.vwap, '₹');
    setVal('ind-stoch', ind.stoch_k);
    setVal('ind-support', ind.support, '₹');
    setVal('ind-resist', ind.resistance, '₹');

    // RSI color coding
    const rsiChip = document.getElementById('chip-rsi');
    if (rsiChip && ind.rsi) {
        rsiChip.className = 'indicator-chip';
        if (ind.rsi > 70) rsiChip.classList.add('chip-danger');
        else if (ind.rsi < 30) rsiChip.classList.add('chip-success');
        else rsiChip.classList.add('chip-neutral');
    }

    // MACD color coding
    const macdChip = document.getElementById('chip-macd');
    if (macdChip && ind.macd !== null) {
        macdChip.className = 'indicator-chip';
        if (ind.macd > 0) macdChip.classList.add('chip-success');
        else macdChip.classList.add('chip-danger');
    }

    // ADX color coding
    const adxChip = document.getElementById('chip-adx');
    if (adxChip && ind.adx) {
        adxChip.className = 'indicator-chip';
        if (ind.adx > 25) adxChip.classList.add('chip-success');
        else adxChip.classList.add('chip-neutral');
    }
}

function typeWriter(text, element, i = 0) {
    if (i < text.length) {
        element.textContent += text.charAt(i);
        setTimeout(() => typeWriter(text, element, i + 1), 15);
    }
}

// ============ AI PREDICTOR ============
async function generatePrediction() {
    const btn = document.getElementById('predict-btn');
    const symbol = document.getElementById('predict-stock-select').value;

    btn.disabled = true;
    btn.querySelector('.btn-text').textContent = '🔮 Analyzing...';
    showNotification('Generating AI prediction... This may take a moment.', 'info');

    try {
        const response = await fetch(`/api/predict?symbol=${symbol}`);
        const data = await response.json();

        if (response.ok && !data.error) {
            displayPrediction(data);
            document.getElementById('prediction-results').style.display = 'block';
            showNotification('Prediction generated successfully!', 'success');
        } else {
            showNotification('Error: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        showNotification('Network Error: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.querySelector('.btn-text').textContent = '🔮 Generate Prediction';
    }
}

function displayPrediction(data) {
    // Overview
    document.getElementById('pred-current-price').textContent = `₹${data.current_price.toFixed(2)}`;

    const trendEl = document.getElementById('pred-trend');
    trendEl.textContent = data.overall_trend;
    trendEl.className = 'pred-value pred-trend';
    if (data.overall_trend === 'BULLISH') trendEl.classList.add('trend-bullish');
    else if (data.overall_trend === 'BEARISH') trendEl.classList.add('trend-bearish');
    else trendEl.classList.add('trend-neutral');

    const riskEl = document.getElementById('pred-risk');
    riskEl.textContent = data.risk_level;
    riskEl.className = 'pred-value';
    if (data.risk_level === 'LOW') riskEl.style.color = 'var(--success)';
    else if (data.risk_level === 'MODERATE') riskEl.style.color = 'var(--warning)';
    else riskEl.style.color = 'var(--danger)';

    const recEl = document.getElementById('pred-recommendation');
    recEl.textContent = data.recommendation;
    recEl.className = 'pred-value pred-recommendation';
    if (data.recommendation.includes('BUY')) recEl.classList.add('rec-buy');
    else if (data.recommendation.includes('SELL')) recEl.classList.add('rec-sell');
    else recEl.classList.add('rec-hold');

    // Price Targets
    const pred = data.predictions;
    if (pred) {
        setPredTarget('1w', pred['1_week']);
        setPredTarget('1m', pred['1_month']);
        setPredTarget('3m', pred['3_months']);
    }

    // Key Levels
    document.getElementById('pred-entry').textContent = `₹${data.best_entry_price?.toFixed(2) || '--'}`;
    document.getElementById('pred-stoploss').textContent = `₹${data.stop_loss?.toFixed(2) || '--'}`;

    if (data.support_levels) {
        data.support_levels.forEach((s, i) => {
            const el = document.getElementById(`pred-sup${i + 1}`);
            if (el) el.textContent = `₹${s.toFixed(2)}`;
        });
    }
    if (data.resistance_levels) {
        data.resistance_levels.forEach((r, i) => {
            const el = document.getElementById(`pred-res${i + 1}`);
            if (el) el.textContent = `₹${r.toFixed(2)}`;
        });
    }

    // Risk & Stats
    const trendStrength = data.trend_strength || 0;
    document.getElementById('pred-trend-bar').style.width = `${trendStrength * 10}%`;
    document.getElementById('pred-trend-val').textContent = `${trendStrength}/10`;

    const riskScore = data.risk_score || 0;
    document.getElementById('pred-risk-bar').style.width = `${riskScore * 10}%`;
    document.getElementById('pred-risk-val').textContent = `${riskScore}/10`;

    document.getElementById('pred-rsi-val').textContent = data.rsi || '--';
    document.getElementById('pred-vol-val').textContent = data.volatility ? `${data.volatility}%` : '--';
    document.getElementById('pred-7d-ret').textContent = data.weekly_return !== undefined ? `${data.weekly_return}%` : '--';
    document.getElementById('pred-30d-ret').textContent = data.monthly_return !== undefined ? `${data.monthly_return}%` : '--';
    document.getElementById('pred-vol-ratio').textContent = data.volume_ratio ? `${data.volume_ratio}x` : '--';
    document.getElementById('pred-horizon').textContent = data.investment_horizon || '--';

    // Color return values
    const ret7dEl = document.getElementById('pred-7d-ret');
    ret7dEl.style.color = data.weekly_return >= 0 ? 'var(--success)' : 'var(--danger)';
    const ret30dEl = document.getElementById('pred-30d-ret');
    ret30dEl.style.color = data.monthly_return >= 0 ? 'var(--success)' : 'var(--danger)';

    // AI Analysis
    document.getElementById('pred-detailed-analysis').textContent = data.detailed_analysis || '--';
    document.getElementById('pred-indicators-summary').textContent = data.key_indicators_summary || '--';
    document.getElementById('pred-catalysts').textContent = data.catalysts || '--';
    document.getElementById('pred-risks').textContent = data.risks || '--';
}

function setPredTarget(prefix, pred) {
    if (!pred) return;
    const priceEl = document.getElementById(`pred-${prefix}-price`);
    const rangeEl = document.getElementById(`pred-${prefix}-range`);
    const dirEl = document.getElementById(`pred-${prefix}-dir`);
    const confEl = document.getElementById(`pred-${prefix}-conf`);
    const confValEl = document.getElementById(`pred-${prefix}-conf-val`);

    priceEl.textContent = `₹${pred.target_price?.toFixed(2) || '--'}`;
    rangeEl.textContent = `Range: ₹${pred.range_low?.toFixed(2) || '--'} - ₹${pred.range_high?.toFixed(2) || '--'}`;

    dirEl.textContent = pred.direction;
    dirEl.className = 'target-direction';
    if (pred.direction === 'UP') dirEl.classList.add('dir-up');
    else if (pred.direction === 'DOWN') dirEl.classList.add('dir-down');
    else dirEl.classList.add('dir-sideways');

    const confPercent = (pred.confidence || 0) * 100;
    confEl.style.width = `${confPercent}%`;
    confValEl.textContent = `${confPercent.toFixed(0)}%`;
}

// ============ STOCK SCREENER ============
async function runScreener() {
    const btn = document.getElementById('screen-btn');
    const criteria = document.getElementById('screener-criteria').value;

    btn.disabled = true;
    btn.querySelector('.btn-text').textContent = '🔍 Scanning...';
    showNotification('Scanning market... This may take a moment.', 'info');

    try {
        const response = await fetch(`/api/screener?criteria=${criteria}`);
        const data = await response.json();

        if (response.ok && !data.error) {
            displayScreenerResults(data, criteria);
            showNotification(`Found ${data.length} stocks!`, 'success');
        } else {
            showNotification('Error: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        showNotification('Network Error: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.querySelector('.btn-text').textContent = '🔍 Scan Market';
    }
}

function displayScreenerResults(data, criteria) {
    const container = document.getElementById('screener-results');

    if (!data || data.length === 0) {
        container.innerHTML = '<p class="empty-state">No stocks matched the criteria.</p>';
        return;
    }

    let html = '<div class="screener-table-wrap"><table class="screener-table"><thead><tr>';
    html += '<th>Rank</th><th>Symbol</th><th>Name</th><th>Sector</th><th>Price (₹)</th>';
    html += '<th>7D Return</th><th>30D Return</th><th>RSI</th><th>Vol Ratio</th><th>Score</th>';
    html += '</tr></thead><tbody>';

    data.forEach((stock, index) => {
        const ret7dClass = stock.returns_7d >= 0 ? 'change-positive' : 'change-negative';
        const ret30dClass = stock.returns_30d >= 0 ? 'change-positive' : 'change-negative';
        const rsiClass = stock.rsi > 70 ? 'rsi-overbought' : stock.rsi < 30 ? 'rsi-oversold' : '';

        html += `<tr class="screener-row ${index < 3 ? 'top-pick' : ''}">
            <td class="rank">${index + 1}</td>
            <td class="symbol-cell">${stock.symbol.replace('.NS', '')}</td>
            <td>${stock.name}</td>
            <td><span class="sector-tag">${stock.sector}</span></td>
            <td class="price-cell">₹${stock.price.toFixed(2)}</td>
            <td class="${ret7dClass}">${stock.returns_7d >= 0 ? '+' : ''}${stock.returns_7d}%</td>
            <td class="${ret30dClass}">${stock.returns_30d >= 0 ? '+' : ''}${stock.returns_30d}%</td>
            <td class="${rsiClass}">${stock.rsi}</td>
            <td>${stock.volume_ratio}x</td>
            <td class="score-cell">${stock.score}</td>
        </tr>`;
    });

    html += '</tbody></table></div>';
    container.innerHTML = html;
}

// ============ PORTFOLIO MANAGEMENT ============
async function loadPortfolio() {
    try {
        const response = await fetch('/api/portfolio');
        const portfolio = await response.json();
        const listEl = document.getElementById('portfolio-list');

        if (portfolio.length === 0) {
            listEl.innerHTML = '<p class="empty-state">No holdings yet. Add stocks to your portfolio!</p>';
            document.getElementById('total-value').textContent = '₹0.00';
            document.getElementById('total-pl').textContent = '₹0.00';
            return;
        }

        listEl.innerHTML = '';
        let totalValue = 0;

        portfolio.forEach(item => {
            const itemValue = item.quantity * item.buy_price;
            totalValue += itemValue;

            const div = document.createElement('div');
            div.className = 'portfolio-item';
            div.innerHTML = `
                <div class="portfolio-info">
                    <strong>${item.symbol}</strong>
                    <span>Qty: ${item.quantity} @ ₹${item.buy_price.toFixed(2)}</span>
                </div>
                <div class="portfolio-actions">
                    <span class="portfolio-value">₹${itemValue.toFixed(2)}</span>
                    <button class="btn-delete" onclick="deletePortfolioItem(${item.id})">🗑️</button>
                </div>
            `;
            listEl.appendChild(div);
        });

        document.getElementById('total-value').textContent = `₹${totalValue.toFixed(2)}`;
    } catch (error) {
        showNotification('Error loading portfolio: ' + error.message, 'error');
    }
}

async function addToPortfolio() {
    const symbol = document.getElementById('portfolio-symbol').value.trim().toUpperCase();
    const quantity = parseInt(document.getElementById('portfolio-quantity').value);
    const price = parseFloat(document.getElementById('portfolio-price').value);

    if (!symbol || !quantity || !price) {
        showNotification('Please fill all fields', 'error');
        return;
    }

    try {
        const response = await fetch('/api/portfolio', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, quantity, buy_price: price })
        });

        if (response.ok) {
            showNotification('Added to portfolio!', 'success');
            document.getElementById('portfolio-symbol').value = '';
            document.getElementById('portfolio-quantity').value = '';
            document.getElementById('portfolio-price').value = '';
            loadPortfolio();
        }
    } catch (error) {
        showNotification('Network error: ' + error.message, 'error');
    }
}

async function deletePortfolioItem(id) {
    try {
        const response = await fetch(`/api/portfolio?id=${id}`, { method: 'DELETE' });
        if (response.ok) {
            showNotification('Removed from portfolio', 'success');
            loadPortfolio();
        }
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    }
}

// ============ ALERTS MANAGEMENT ============
async function loadAlerts() {
    try {
        const response = await fetch('/api/alerts');
        const alerts = await response.json();
        const listEl = document.getElementById('alerts-list');

        if (alerts.length === 0) {
            listEl.innerHTML = '<p class="empty-state">No active alerts. Create one to get notified!</p>';
            return;
        }

        listEl.innerHTML = '';
        alerts.forEach(alert => {
            const div = document.createElement('div');
            div.className = 'alert-item';
            div.innerHTML = `
                <div class="alert-info">
                    <strong>${alert.symbol}</strong>
                    <span>${alert.type === 'above' ? '↑' : '↓'} ₹${alert.price.toFixed(2)}</span>
                </div>
                <button class="btn-delete" onclick="deleteAlert(${alert.id})">🗑️</button>
            `;
            listEl.appendChild(div);
        });
    } catch (error) {
        showNotification('Error loading alerts: ' + error.message, 'error');
    }
}

async function createAlert() {
    const symbol = document.getElementById('alert-symbol').value;
    const type = document.getElementById('alert-type').value;
    const price = parseFloat(document.getElementById('alert-price').value);

    if (!price) {
        showNotification('Please enter a price', 'error');
        return;
    }

    try {
        const response = await fetch('/api/alerts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, type, price })
        });

        if (response.ok) {
            showNotification('Alert created!', 'success');
            document.getElementById('alert-price').value = '';
            loadAlerts();
        }
    } catch (error) {
        showNotification('Network error: ' + error.message, 'error');
    }
}

async function deleteAlert(id) {
    try {
        const response = await fetch(`/api/alerts?id=${id}`, { method: 'DELETE' });
        if (response.ok) {
            showNotification('Alert deleted', 'success');
            loadAlerts();
        }
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    }
}

// ============ HISTORY ============
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const history = await response.json();
        const listEl = document.getElementById('history-list');

        if (history.length === 0) {
            listEl.innerHTML = '<p class="empty-state">No analysis history yet. Run your first analysis!</p>';
            return;
        }

        listEl.innerHTML = '';
        [...history].reverse().forEach(entry => {
            const date = new Date(entry.timestamp);
            const div = document.createElement('div');
            div.className = `history-item signal-${entry.signal.action.toLowerCase()}`;
            div.innerHTML = `
                <div class="history-header">
                    <strong>${entry.symbol}</strong>
                    <span class="history-time">${date.toLocaleString()}</span>
                </div>
                <div class="history-details">
                    <span class="history-price">₹${entry.price.toFixed(2)}</span>
                    <span class="history-signal ${entry.signal.action.toLowerCase()}">${entry.signal.action}</span>
                    <span class="history-confidence">${(entry.signal.confidence * 100).toFixed(0)}%</span>
                </div>
                <p class="history-reasoning">${entry.signal.reasoning}</p>
            `;
            listEl.appendChild(div);
        });
    } catch (error) {
        showNotification('Error loading history: ' + error.message, 'error');
    }
}

// ============ EXPORT ============
function showExportMenu() {
    const menu = confirm('Export as CSV? (OK for CSV, Cancel for JSON)');
    if (menu === true) {
        window.location.href = '/api/export/csv';
        showNotification('Downloading CSV...', 'success');
    } else {
        window.location.href = '/api/export/json';
        showNotification('Downloading JSON...', 'success');
    }
}

// ============ CHART ============
function initChart() {
    const ctx = document.getElementById('marketChart').getContext('2d');
    marketChart = new Chart(ctx, {
        type: 'line',
        data: { labels: [], datasets: [] },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    labels: { color: '#a0a0b0', font: { family: 'Outfit', size: 11 } }
                },
                tooltip: {
                    backgroundColor: 'rgba(11, 11, 21, 0.9)',
                    borderColor: 'rgba(0, 243, 255, 0.3)',
                    borderWidth: 1,
                    titleColor: '#00f3ff',
                    bodyColor: '#e0e0ff',
                    padding: 12,
                    cornerRadius: 8,
                }
            },
            scales: {
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#a0a0b0', font: { family: 'Outfit' } }
                },
                x: {
                    grid: { display: false },
                    ticks: { display: false }
                }
            }
        }
    });
}

function renderChart(marketData, chartType) {
    if (!marketChart) return;

    const labels = marketData.labels;
    let datasets = [];

    switch (chartType) {
        case 'price':
            datasets = [
                {
                    label: 'Price',
                    data: marketData.prices,
                    borderColor: '#00f3ff',
                    backgroundColor: 'rgba(0, 243, 255, 0.08)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                },
                {
                    label: 'SMA 20',
                    data: marketData.sma,
                    borderColor: '#bf00ff',
                    borderWidth: 1.5,
                    borderDash: [5, 5],
                    pointRadius: 0,
                    fill: false,
                },
                {
                    label: 'BB Upper',
                    data: marketData.bb_upper,
                    borderColor: 'rgba(255, 204, 0, 0.4)',
                    borderWidth: 1,
                    borderDash: [3, 3],
                    pointRadius: 0,
                    fill: false,
                },
                {
                    label: 'BB Lower',
                    data: marketData.bb_lower,
                    borderColor: 'rgba(255, 204, 0, 0.4)',
                    borderWidth: 1,
                    borderDash: [3, 3],
                    pointRadius: 0,
                    fill: '-1',
                    backgroundColor: 'rgba(255, 204, 0, 0.05)',
                },
                {
                    label: 'EMA 12',
                    data: marketData.ema_12,
                    borderColor: 'rgba(0, 255, 157, 0.5)',
                    borderWidth: 1,
                    pointRadius: 0,
                    fill: false,
                }
            ];
            break;

        case 'macd':
            datasets = [
                {
                    label: 'MACD',
                    data: marketData.macd,
                    borderColor: '#00f3ff',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false,
                },
                {
                    label: 'Signal',
                    data: marketData.macd_signal,
                    borderColor: '#ff0055',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false,
                },
                {
                    label: 'Histogram',
                    data: marketData.macd_histogram,
                    type: 'bar',
                    backgroundColor: marketData.macd_histogram?.map(v =>
                        v >= 0 ? 'rgba(0, 255, 157, 0.5)' : 'rgba(255, 0, 85, 0.5)'
                    ),
                    borderWidth: 0,
                }
            ];
            break;

        case 'rsi':
            datasets = [
                {
                    label: 'RSI',
                    data: marketData.rsi,
                    borderColor: '#bf00ff',
                    backgroundColor: 'rgba(191, 0, 255, 0.1)',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: true,
                }
            ];
            // Add overbought/oversold reference lines via annotation plugin or just overlay
            break;

        case 'volume':
            datasets = [
                {
                    label: 'Volume',
                    data: marketData.volume,
                    type: 'bar',
                    backgroundColor: 'rgba(0, 243, 255, 0.3)',
                    borderColor: 'rgba(0, 243, 255, 0.6)',
                    borderWidth: 1,
                }
            ];
            break;

        case 'stochastic':
            datasets = [
                {
                    label: 'Stoch %K',
                    data: marketData.stoch_k,
                    borderColor: '#00f3ff',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false,
                },
                {
                    label: 'Stoch %D',
                    data: marketData.stoch_d,
                    borderColor: '#ff0055',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false,
                }
            ];
            break;
    }

    marketChart.data.labels = labels;
    marketChart.data.datasets = datasets;
    marketChart.update('none');
}

// ============ NOTIFICATIONS ============
function showNotification(message, type = 'info') {
    const toast = document.getElementById('notification-toast');
    toast.textContent = message;
    toast.className = `notification-toast show ${type}`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
