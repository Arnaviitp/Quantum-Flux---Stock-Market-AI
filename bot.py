import os
import json
import time
import numpy as np
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Configuration
SYMBOL = "RELIANCE.NS"  # Indian Stock Market (NSE)
INTERVAL = "1h"     # 1 hour candles
PERIOD = "5d"       # Last 5 days of data
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Groq client (primary)
groq_client = None
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    print("⚠️ GROQ_API_KEY not found. Groq will not be available.")

# Initialize Google Gemini client (backup)
gemini_model = None
if GOOGLE_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        gemini_model = genai.GenerativeModel("gemini-pro")
        print("✅ Google Gemini configured as backup AI provider.")
    except Exception as e:
        print(f"⚠️ Failed to configure Gemini: {e}")
else:
    print("⚠️ GOOGLE_API_KEY not found. Gemini backup will not be available.")

if not groq_client and not gemini_model:
    raise ValueError("No AI provider configured! Set GROQ_API_KEY or GOOGLE_API_KEY in .env")

# Keep backward compat
client = groq_client

# ============ UNIFIED AI CALLER ============
def call_ai(system_prompt, user_prompt, temperature=0.1, max_tokens=2000):
    """
    Calls Groq first, falls back to Google Gemini if Groq fails.
    Returns the raw text response from the AI.
    """
    # Try Groq first
    if groq_client:
        try:
            completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=temperature,
                max_tokens=max_tokens,
            )
            response = completion.choices[0].message.content
            print("  ✅ AI response from Groq")
            return response
        except Exception as groq_err:
            print(f"  ⚠️ Groq failed: {groq_err}")
            print("  🔄 Falling back to Google Gemini...")

    # Fallback to Gemini
    if gemini_model:
        try:
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"
            response = gemini_model.generate_content(
                combined_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
            )
            print("  ✅ AI response from Google Gemini (backup)")
            return response.text
        except Exception as gemini_err:
            print(f"  ❌ Gemini also failed: {gemini_err}")
            raise Exception(f"Both AI providers failed. Groq error / Gemini error: {gemini_err}")

    raise Exception("No AI provider available")

# ============ STOCK LISTS ============
STOCK_UNIVERSE = {
    "RELIANCE.NS": {"name": "Reliance Industries", "sector": "Energy"},
    "TCS.NS": {"name": "TCS", "sector": "IT"},
    "HDFCBANK.NS": {"name": "HDFC Bank", "sector": "Banking"},
    "INFY.NS": {"name": "Infosys", "sector": "IT"},
    "ICICIBANK.NS": {"name": "ICICI Bank", "sector": "Banking"},
    "SBIN.NS": {"name": "SBI", "sector": "Banking"},
    "BHARTIARTL.NS": {"name": "Bharti Airtel", "sector": "Telecom"},
    "ITC.NS": {"name": "ITC", "sector": "FMCG"},
    "TATAMOTORS.NS": {"name": "Tata Motors", "sector": "Auto"},
    "LICI.NS": {"name": "LIC India", "sector": "Insurance"},
    "WIPRO.NS": {"name": "Wipro", "sector": "IT"},
    "HCLTECH.NS": {"name": "HCL Tech", "sector": "IT"},
    "MARUTI.NS": {"name": "Maruti Suzuki", "sector": "Auto"},
    "BAJFINANCE.NS": {"name": "Bajaj Finance", "sector": "Finance"},
    "LT.NS": {"name": "L&T", "sector": "Infrastructure"},
}

def _fix_symbol(symbol):
    """Fix .NS to .BO for Yahoo Finance compatibility."""
    return symbol.replace('.NS', '.BO') if symbol.endswith('.NS') else symbol

# ============ DATA FETCHING ============
def fetch_market_data(symbol, period, interval):
    """
    Fetches historical data using yfinance with advanced indicators.
    """
    yf_symbol = _fix_symbol(symbol)
    print(f"Fetching data for {yf_symbol}...")
    
    # Try fetching hourly data first
    df = yf.download(yf_symbol, period=period, interval=interval, progress=False, auto_adjust=True)
    
    # If hourly data is empty, fallback to daily data
    if df.empty:
        print(f"Hourly data unavailable for {yf_symbol}. Falling back to daily data...")
        df = yf.download(yf_symbol, period="1mo", interval="1d", progress=False, auto_adjust=True)
    
    if df.empty:
        print("No data found.")
        return None

    # Handle MultiIndex columns (yfinance sometimes returns (Price, Ticker))
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # ===== TECHNICAL INDICATORS =====
    close = df['Close']
    high = df['High']
    low = df['Low']
    volume = df['Volume']
    
    # SMA (Simple Moving Average)
    df['SMA_20'] = close.rolling(window=20).mean()
    df['SMA_50'] = close.rolling(window=50).mean()
    
    # EMA (Exponential Moving Average)
    df['EMA_12'] = close.ewm(span=12, adjust=False).mean()
    df['EMA_26'] = close.ewm(span=26, adjust=False).mean()
    df['EMA_9'] = close.ewm(span=9, adjust=False).mean()
    
    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
    
    # RSI
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    bb_sma = close.rolling(window=20).mean()
    bb_std = close.rolling(window=20).std()
    df['BB_Upper'] = bb_sma + (bb_std * 2)
    df['BB_Middle'] = bb_sma
    df['BB_Lower'] = bb_sma - (bb_std * 2)
    df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
    
    # Stochastic Oscillator
    low_14 = low.rolling(window=14).min()
    high_14 = high.rolling(window=14).max()
    df['Stoch_K'] = 100 * ((close - low_14) / (high_14 - low_14))
    df['Stoch_D'] = df['Stoch_K'].rolling(window=3).mean()
    
    # ATR (Average True Range) - Volatility
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(window=14).mean()
    
    # OBV (On-Balance Volume)
    obv = [0]
    for i in range(1, len(df)):
        if close.iloc[i] > close.iloc[i-1]:
            obv.append(obv[-1] + volume.iloc[i])
        elif close.iloc[i] < close.iloc[i-1]:
            obv.append(obv[-1] - volume.iloc[i])
        else:
            obv.append(obv[-1])
    df['OBV'] = obv
    
    # VWAP (Volume Weighted Average Price)
    df['VWAP'] = (volume * (high + low + close) / 3).cumsum() / volume.cumsum()
    
    # ADX (Average Directional Index) - Trend Strength
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    minus_dm = abs(minus_dm)
    
    plus_di = 100 * (plus_dm.ewm(alpha=1/14).mean() / df['ATR'])
    minus_di = 100 * (minus_dm.ewm(alpha=1/14).mean() / df['ATR'])
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    df['ADX'] = dx.ewm(alpha=1/14).mean()
    
    # Support and Resistance (pivot points)
    df['Pivot'] = (high + low + close) / 3
    df['Support_1'] = 2 * df['Pivot'] - high
    df['Resistance_1'] = 2 * df['Pivot'] - low
    
    return df

def fetch_extended_data(symbol, period="3mo", interval="1d"):
    """Fetch extended historical data for prediction analysis."""
    yf_symbol = _fix_symbol(symbol)
    df = yf.download(yf_symbol, period=period, interval=interval, progress=False, auto_adjust=True)
    
    if df.empty:
        df = yf.download(yf_symbol, period="6mo", interval="1d", progress=False, auto_adjust=True)
    
    if df.empty:
        return None
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    return df

def fetch_market_indices():
    """
    Fetches current data for NIFTY 50 and SENSEX.
    """
    indices = {
        "NIFTY 50": "^NSEI",
        "SENSEX": "^BSESN"
    }
    
    data = {}
    
    for name, symbol in indices.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else hist['Open'].iloc[-1]
                change = current_price - prev_close
                percent_change = (change / prev_close) * 100
                
                data[name] = {
                    "price": current_price,
                    "change": change,
                    "percent_change": percent_change
                }
            else:
                data[name] = None
        except Exception as e:
            print(f"Error fetching {name}: {e}")
            data[name] = None
            
    return data

# ============ AI ANALYSIS ============
def get_trading_signal(market_data, symbol):
    """
    Sends the recent market data to Groq to get a trading signal.
    """
    recent_data = market_data.tail(10).to_string()
    
    system_prompt = """
    You are an elite AI Trading Bot. Your job is to analyze the provided OHLCV market data and technical indicators (SMA, RSI, MACD, Bollinger Bands, Stochastic, ATR, ADX, VWAP).
    
    Based on the data, you must decide to:
    - BUY (if the trend is bullish and indicators support it)
    - SELL (if the trend is bearish and indicators support it)
    - HOLD (if the market is sideways or uncertain)
    
    You MUST return your response in the following strict JSON format:
    {
        "action": "BUY" | "SELL" | "HOLD",
        "confidence": <number between 0 and 1>,
        "reasoning": "<brief explanation of why>"
    }
    Do not include any text outside the JSON.
    """
    
    user_prompt = f"""
    Analyze the following market data for {symbol}:
    
    {recent_data}
    
    Provide your trading decision.
    """
    
    try:
        response_content = call_ai(system_prompt, user_prompt, temperature=0.1)
        return response_content
    except Exception as e:
        error_msg = str(e).replace('"', "'").replace('\n', ' ')
        # Shorten error message if it's too long (like quota errors)
        if len(error_msg) > 150:
            error_msg = error_msg[:147] + "..."
        return f'{{"action": "HOLD", "confidence": 0, "reasoning": "AI Provider Error (Rate Limit/Quota): {error_msg}"}}'

# ============ AI MARKET PREDICTION ============
def get_market_prediction(symbol):
    """
    Uses AI to provide deep market analysis and future predictions with price targets.
    """
    # Fetch extended data for better analysis
    df = fetch_extended_data(symbol, period="3mo", interval="1d")
    if df is None:
        return {"error": "No data available"}
    
    # Handle MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    close = df['Close']
    high = df['High']
    low = df['Low']
    volume = df['Volume']
    
    # Calculate key stats
    current_price = float(close.iloc[-1])
    price_30d_ago = float(close.iloc[-30]) if len(close) >= 30 else float(close.iloc[0])
    price_7d_ago = float(close.iloc[-7]) if len(close) >= 7 else float(close.iloc[0])
    
    monthly_return = ((current_price - price_30d_ago) / price_30d_ago) * 100
    weekly_return = ((current_price - price_7d_ago) / price_7d_ago) * 100
    
    # Volatility
    daily_returns = close.pct_change().dropna()
    volatility = float(daily_returns.std() * np.sqrt(252) * 100)  # Annualized
    
    # Calculate indicators for the extended data
    sma_20 = close.rolling(20).mean()
    sma_50 = close.rolling(50).mean()
    ema_12 = close.ewm(span=12).mean()
    ema_26 = close.ewm(span=26).mean()
    macd = ema_12 - ema_26
    macd_signal = macd.ewm(span=9).mean()
    
    # RSI
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # Bollinger
    bb_sma = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    bb_upper = bb_sma + (bb_std * 2)
    bb_lower = bb_sma - (bb_std * 2)
    
    # ATR
    tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
    atr = float(tr.rolling(14).mean().iloc[-1])
    
    # Volume analysis
    avg_volume = float(volume.tail(20).mean())
    recent_volume = float(volume.iloc[-1])
    volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
    
    # Compile summary
    analysis_summary = f"""
    === {symbol} Market Analysis Summary ===
    
    PRICE DATA:
    Current Price: ₹{current_price:.2f}
    7-Day Return: {weekly_return:.2f}%
    30-Day Return: {monthly_return:.2f}%
    52-Week High: ₹{float(high.tail(252).max()):.2f}
    52-Week Low: ₹{float(low.tail(252).min()):.2f}
    
    TECHNICAL INDICATORS (Latest):
    SMA 20: ₹{float(sma_20.iloc[-1]):.2f}
    SMA 50: ₹{float(sma_50.iloc[-1]):.2f} 
    MACD: {float(macd.iloc[-1]):.4f}
    MACD Signal: {float(macd_signal.iloc[-1]):.4f}
    MACD Histogram: {float((macd - macd_signal).iloc[-1]):.4f}
    RSI (14): {float(rsi.iloc[-1]):.2f}
    Bollinger Upper: ₹{float(bb_upper.iloc[-1]):.2f}
    Bollinger Lower: ₹{float(bb_lower.iloc[-1]):.2f}
    ATR (14): ₹{atr:.2f}
    
    TREND:
    Price vs SMA20: {"ABOVE" if current_price > float(sma_20.iloc[-1]) else "BELOW"}
    Price vs SMA50: {"ABOVE" if current_price > float(sma_50.iloc[-1]) else "BELOW"}
    SMA20 vs SMA50: {"GOLDEN CROSS" if float(sma_20.iloc[-1]) > float(sma_50.iloc[-1]) else "DEATH CROSS"}
    MACD vs Signal: {"BULLISH" if float(macd.iloc[-1]) > float(macd_signal.iloc[-1]) else "BEARISH"}
    
    VOLATILITY:
    Annualized Volatility: {volatility:.2f}%
    ATR (14): ₹{atr:.2f}
    
    VOLUME:
    Current Volume: {recent_volume:,.0f}
    20-Day Avg Volume: {avg_volume:,.0f}
    Volume Ratio: {volume_ratio:.2f}x
    
    RECENT PRICE ACTION (Last 10 trading days):
    {df.tail(10)[['Close', 'Volume']].to_string()}
    """
    
    prediction_prompt = f"""You are a world-class quantitative financial analyst and market predictor AI.
    
    Analyze the following comprehensive market data and technical indicators for {symbol}:
    
    {analysis_summary}
    
    Based on your deep analysis, provide:
    1. Future price predictions with specific price targets
    2. Risk assessment 
    3. Investment recommendation with time horizons
    4. Key support and resistance levels
    5. Potential catalysts and risks
    
    You MUST return your response in this exact JSON format:
    {{
        "overall_trend": "BULLISH" | "BEARISH" | "NEUTRAL",
        "trend_strength": <number 1-10>,
        "risk_level": "LOW" | "MODERATE" | "HIGH" | "VERY HIGH",
        "risk_score": <number 1-10>,
        "predictions": {{
            "1_week": {{
                "target_price": <number>,
                "direction": "UP" | "DOWN" | "SIDEWAYS",
                "confidence": <number 0-1>,
                "range_low": <number>,
                "range_high": <number>
            }},
            "1_month": {{
                "target_price": <number>,
                "direction": "UP" | "DOWN" | "SIDEWAYS",
                "confidence": <number 0-1>,
                "range_low": <number>,
                "range_high": <number>
            }},
            "3_months": {{
                "target_price": <number>,
                "direction": "UP" | "DOWN" | "SIDEWAYS",
                "confidence": <number 0-1>,
                "range_low": <number>,
                "range_high": <number>
            }}
        }},
        "support_levels": [<number>, <number>, <number>],
        "resistance_levels": [<number>, <number>, <number>],
        "best_entry_price": <number>,
        "stop_loss": <number>,
        "recommendation": "STRONG BUY" | "BUY" | "HOLD" | "SELL" | "STRONG SELL",
        "investment_horizon": "SHORT TERM" | "MEDIUM TERM" | "LONG TERM",
        "key_indicators_summary": "<brief summary of what key indicators suggest>",
        "catalysts": "<potential positive catalysts>",
        "risks": "<potential risks and red flags>",
        "detailed_analysis": "<comprehensive 3-4 sentence analysis explaining the market dynamics, trend, and projection reasoning>"
    }}
    
    Do not include any text outside the JSON. Be precise with numbers.
    """
    
    try:
        system_msg = "You are an elite quantitative financial analyst AI. You analyze market data and provide precise, data-driven predictions and price targets. Always respond in exact JSON format only, no other text."
        response = call_ai(system_msg, prediction_prompt, temperature=0.15, max_tokens=2000)
        
        clean = response.replace("```json", "").replace("```", "").strip()
        
        # Try direct parse first
        prediction = None
        try:
            prediction = json.loads(clean)
        except json.JSONDecodeError:
            # Try to extract JSON object from the response
            import re
            # Find the outermost JSON object
            brace_count = 0
            start_idx = None
            for i, ch in enumerate(clean):
                if ch == '{':
                    if start_idx is None:
                        start_idx = i
                    brace_count += 1
                elif ch == '}':
                    brace_count -= 1
                    if brace_count == 0 and start_idx is not None:
                        try:
                            prediction = json.loads(clean[start_idx:i+1])
                            break
                        except json.JSONDecodeError:
                            start_idx = None
                            continue
        
        if prediction is None:
            return {"error": "Failed to parse AI prediction response"}
        
        # Add additional computed data
        prediction["current_price"] = current_price
        prediction["weekly_return"] = round(weekly_return, 2)
        prediction["monthly_return"] = round(monthly_return, 2)
        prediction["volatility"] = round(volatility, 2)
        prediction["volume_ratio"] = round(volume_ratio, 2)
        prediction["rsi"] = round(float(rsi.iloc[-1]), 2)
        prediction["macd_value"] = round(float(macd.iloc[-1]), 4)
        prediction["atr"] = round(atr, 2)
        
        return prediction
        
    except Exception as e:
        error_msg = str(e).replace('\n', ' ')
        if len(error_msg) > 100:
            error_msg = error_msg[:97] + "..."
        return {"error": f"AI Rate Limit Error: {error_msg}"}

# ============ STOCK SCREENER ============
def screen_stocks(criteria="momentum"):
    """Quick screen of stocks based on criteria."""
    results = []
    
    for symbol, info in STOCK_UNIVERSE.items():
        try:
            yf_symbol = _fix_symbol(symbol)
            df = yf.download(yf_symbol, period="1mo", interval="1d", progress=False, auto_adjust=True)
            
            if df.empty:
                continue
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            close = df['Close']
            current_price = float(close.iloc[-1])
            
            # Calculate basic metrics
            returns_7d = float(((close.iloc[-1] - close.iloc[-7]) / close.iloc[-7]) * 100) if len(close) >= 7 else 0
            returns_30d = float(((close.iloc[-1] - close.iloc[0]) / close.iloc[0]) * 100)
            
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_val = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50
            
            # Volume trend
            vol = df['Volume']
            avg_vol = float(vol.tail(20).mean())
            recent_vol = float(vol.iloc[-1])
            vol_ratio = recent_vol / avg_vol if avg_vol > 0 else 1
            
            # Score based on criteria
            score = 0
            if criteria == "momentum":
                score = returns_7d * 2 + returns_30d + (rsi_val - 50) * 0.1
            elif criteria == "oversold":
                score = (30 - rsi_val) if rsi_val < 40 else -(rsi_val - 40)
            elif criteria == "volume_surge":
                score = vol_ratio * 10
            
            results.append({
                "symbol": symbol,
                "name": info["name"],
                "sector": info["sector"],
                "price": round(current_price, 2),
                "returns_7d": round(returns_7d, 2),
                "returns_30d": round(returns_30d, 2),
                "rsi": round(rsi_val, 2),
                "volume_ratio": round(vol_ratio, 2),
                "score": round(score, 2)
            })
        except Exception as e:
            print(f"Error screening {symbol}: {e}")
            continue
    
    # Sort by score descending
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

# ============ SECTOR ANALYSIS ============
def get_sector_performance():
    """Get performance by sector."""
    sectors = {}
    
    for symbol, info in STOCK_UNIVERSE.items():
        sector = info["sector"]
        if sector not in sectors:
            sectors[sector] = {"stocks": [], "total_return": 0, "count": 0}
        
        try:
            yf_symbol = _fix_symbol(symbol)
            df = yf.download(yf_symbol, period="1mo", interval="1d", progress=False, auto_adjust=True)
            
            if df.empty:
                continue
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            close = df['Close']
            ret = float(((close.iloc[-1] - close.iloc[0]) / close.iloc[0]) * 100)
            
            sectors[sector]["stocks"].append({
                "symbol": symbol,
                "name": info["name"],
                "return": round(ret, 2)
            })
            sectors[sector]["total_return"] += ret
            sectors[sector]["count"] += 1
        except:
            continue
    
    # Calculate averages
    result = {}
    for sector, data in sectors.items():
        if data["count"] > 0:
            result[sector] = {
                "avg_return": round(data["total_return"] / data["count"], 2),
                "stocks": data["stocks"],
                "count": data["count"]
            }
    
    return result

def execute_trade(signal):
    """
    Mock execution of the trade.
    """
    try:
        clean_signal = signal.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_signal)
        
        action = data.get("action")
        confidence = data.get("confidence")
        reasoning = data.get("reasoning")
        
        print("\n" + "="*30)
        print(f"AI DECISION: {action}")
        print(f"CONFIDENCE: {confidence}")
        print(f"REASONING: {reasoning}")
        print("="*30 + "\n")
        
        if action == "BUY" and confidence > 0.7:
            print(f"🚀 Executing BUY Order for {SYMBOL}")
        elif action == "SELL" and confidence > 0.7:
            print(f"🔻 Executing SELL Order for {SYMBOL}")
        else:
            print(f"⏸️ Holding position. (Confidence threshold not met or Hold signal)")
            
    except json.JSONDecodeError:
        print("Failed to parse AI response as JSON.")
        print("Raw Response:", signal)

def main():
    print("Starting Groq AI Trading Bot...")
    
    df = fetch_market_data(SYMBOL, PERIOD, INTERVAL)
    if df is None:
        return

    print("Analyzing market data with Groq AI...")
    signal_json = get_trading_signal(df, SYMBOL)
    
    execute_trade(signal_json)

if __name__ == "__main__":
    main()
