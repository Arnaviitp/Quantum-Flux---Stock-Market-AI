# ⚡ Quantum Flux AI v2.0 — Advanced Trading Intelligence

An AI-powered trading bot for the Indian Stock Market featuring real-time analysis, **future price predictions**, stock screening, portfolio management, and intelligent alerts.

> Built with dual AI providers (Groq + Google Gemini) for maximum reliability.

---

## ✨ Features

### 📊 Market Analysis
- Real-time stock data from Yahoo Finance (15+ Indian stocks)
- AI-powered trading signals — **BUY / SELL / HOLD**
- Confidence metrics for each signal
- Advanced technical indicators dashboard (RSI, MACD, ATR, ADX, VWAP, Stochastic, Bollinger Bands)
- 5 chart types: Price + Bollinger, MACD, RSI, Volume, Stochastic
- AI reasoning with typewriter effect

### 🔮 AI Market Predictor *(New in v2.0)*
- **Future price predictions** with 1-week, 1-month, and 3-month targets
- Price range forecasts with confidence levels
- Risk assessment and risk scoring (1-10)
- Support and resistance levels (3 each)
- Best entry price and stop loss recommendations
- Investment recommendation (Strong Buy → Strong Sell)
- AI-generated catalysts and risk analysis
- Detailed deep analysis with trend strength scoring

### 🔍 Stock Screener *(New in v2.0)*
- Scan 15+ Indian stocks based on technical criteria
- **Momentum** — find trending stocks
- **Oversold** — RSI-based buying opportunities
- **Volume Surge** — unusual volume detection
- Ranked table with sector tags, returns, and scores

### 💼 Portfolio Management
- Track multiple stock holdings
- View total portfolio value
- Add/remove stocks easily

### 🔔 Price Alerts
- Set price alerts for any stock
- Get notified when price crosses thresholds
- Automatic trigger detection during analysis

### 📈 Analysis History
- View past trading signals and AI recommendations
- Review confidence levels and reasoning over time

### ⚡ Additional Features
- **Dual AI** — Groq (primary) + Google Gemini (automatic fallback)
- **Auto-Refresh** — updates every 30 seconds
- **Dark / Light Theme** — persistent preference
- **Data Export** — CSV and JSON
- **Live Market Ticker** — NIFTY 50 & SENSEX with auto-updates

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- A Groq API Key and/or Google Gemini API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Arnaviitp/Quantum-Flux-AI---Trading-Bot.git
   cd Quantum-Flux-AI---Trading-Bot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   # or
   source .venv/bin/activate     # Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys**
   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   ```
   At least one API key is required. Both are recommended for failover.

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to **http://localhost:5000** and start analyzing!

---

## 📁 Project Structure

```
Quantum-Flux-AI---Trading-Bot/
├── .env                  # API keys (NEVER commit!)
├── .gitignore            # Git ignore rules
├── app.py                # Flask backend with all API endpoints
├── bot.py                # AI trading logic, indicators, predictor, screener
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Main web interface (6 tabs)
├── static/
│   ├── script.js         # Frontend JavaScript
│   └── style.css         # Styling, themes, animations
├── README.md             # This file
├── QUICK_START.md        # Quick start guide
├── FEATURE_SUMMARY.md    # Detailed feature documentation
└── DESIGN_DOC.md         # Design documentation
```

---

## 🔧 API Endpoints

| Method   | Endpoint                         | Description                        |
|----------|----------------------------------|------------------------------------|
| `GET`    | `/api/analyze?symbol=TCS.NS`    | Analyze a stock with AI            |
| `GET`    | `/api/predict?symbol=TCS.NS`    | AI future price prediction         |
| `GET`    | `/api/screener?criteria=momentum`| Stock screener                    |
| `GET`    | `/api/sectors`                   | Sector performance analysis        |
| `GET`    | `/api/indices`                   | NIFTY 50 & SENSEX live data       |
| `GET`    | `/api/portfolio`                 | Get portfolio                      |
| `POST`   | `/api/portfolio`                 | Add to portfolio                   |
| `DELETE` | `/api/portfolio?id=1`            | Remove from portfolio              |
| `GET`    | `/api/alerts`                    | Get all alerts                     |
| `POST`   | `/api/alerts`                    | Create alert                       |
| `DELETE` | `/api/alerts?id=1`               | Delete alert                       |
| `GET`    | `/api/history`                   | Get analysis history               |
| `GET`    | `/api/export/json`               | Export all data as JSON            |
| `GET`    | `/api/export/csv`                | Export history as CSV              |

---

## 📊 Supported Stocks

| Symbol           | Name                | Sector         |
|------------------|---------------------|----------------|
| `^NSEI`          | NIFTY 50            | Index          |
| `^BSESN`         | SENSEX              | Index          |
| `RELIANCE.NS`    | Reliance Industries | Energy         |
| `TCS.NS`         | TCS                 | IT             |
| `HDFCBANK.NS`    | HDFC Bank           | Banking        |
| `INFY.NS`        | Infosys             | IT             |
| `ICICIBANK.NS`   | ICICI Bank          | Banking        |
| `SBIN.NS`        | SBI                 | Banking        |
| `BHARTIARTL.NS`  | Bharti Airtel       | Telecom        |
| `ITC.NS`         | ITC                 | FMCG           |
| `WIPRO.NS`       | Wipro               | IT             |
| `HCLTECH.NS`     | HCL Tech            | IT             |
| `MARUTI.NS`      | Maruti Suzuki       | Auto           |
| `BAJFINANCE.NS`  | Bajaj Finance       | Finance        |
| `LT.NS`          | L&T                 | Infrastructure |

---

## 🛠️ Technology Stack

| Layer        | Technology                              |
|--------------|-----------------------------------------|
| **Backend**  | Flask (Python)                          |
| **AI**       | Groq (Llama 3.3 70B) + Google Gemini   |
| **Data**     | yfinance, pandas, numpy                 |
| **Frontend** | Vanilla JavaScript, Chart.js            |
| **Styling**  | Custom CSS with 3D effects & animations |

---

## 🎨 UI Highlights

- 🌌 **Deep Space Grid** — animated 3D perspective background
- 💎 **Glassmorphism Cards** — with 3D tilt on hover
- 🎯 **Indicator Chips** — color-coded RSI/MACD/ADX status
- 📊 **Multi-Chart Views** — switch between 5 chart types
- 🔮 **Prediction Dashboard** — price targets, risk meters, key levels
- 🔍 **Screener Table** — ranked stocks with sector tags
- 🌙 **Dark / Light Theme** — full theme support
- ❤️ **Responsive** — works on desktop, tablet, and mobile

---

## 🔒 Security

- API keys stored in `.env` (git-ignored)
- No hardcoded secrets in source code
- Dual AI provider failover for reliability

---

## ⚠️ Disclaimer

This software is for **educational purposes only**. Do not use it for actual trading without proper understanding and risk management. The developers are not responsible for any financial losses.

---

## 📝 License

This project is for educational purposes. Use at your own risk.

---

**Created with ❤️ by Arnav**
