from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import bot
import json
import pandas as pd
from datetime import datetime
import io
import csv
import traceback

app = Flask(__name__)
CORS(app)

# In-memory storage for demo (use a database in production)
portfolio = []
alerts = []
history = []
prediction_cache = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze')
def analyze():
    try:
        symbol = request.args.get('symbol', bot.SYMBOL)
        
        # 1. Fetch Data
        df = bot.fetch_market_data(symbol, bot.PERIOD, bot.INTERVAL)
        if df is None or df.empty:
            return jsonify({"error": "No data found for this symbol. Please try another stock."}), 500

        # 2. Get Signal
        signal_raw = bot.get_trading_signal(df, symbol)
        
        # 3. Parse Signal - robust parsing for both Groq and Gemini responses
        signal_data = None
        clean_signal = signal_raw.replace("```json", "").replace("```", "").strip()
        
        # Try direct parse
        try:
            signal_data = json.loads(clean_signal)
        except json.JSONDecodeError:
            # Try to extract JSON from the response text
            import re
            json_match = re.search(r'\{[^{}]*"action"[^{}]*\}', clean_signal, re.DOTALL)
            if json_match:
                try:
                    signal_data = json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
        
        if signal_data is None:
            # Final fallback — return a HOLD signal with the raw text as reasoning
            signal_data = {
                "action": "HOLD",
                "confidence": 0.5,
                "reasoning": clean_signal[:300] if clean_signal else "AI response could not be parsed."
            }

        # 4. Prepare Chart Data (Last 50 points)
        chart_df = df.tail(50)
        
        def clean_data(data_list):
            return [x if pd.notna(x) else None for x in data_list]

        chart_data = {
            "labels": chart_df.index.strftime('%Y-%m-%d %H:%M').tolist(),
            "prices": clean_data(chart_df['Close'].tolist()),
            "sma": clean_data(chart_df['SMA_20'].tolist()),
            "sma_50": clean_data(chart_df['SMA_50'].tolist()) if 'SMA_50' in chart_df.columns else [],
            "ema_12": clean_data(chart_df['EMA_12'].tolist()) if 'EMA_12' in chart_df.columns else [],
            "bb_upper": clean_data(chart_df['BB_Upper'].tolist()) if 'BB_Upper' in chart_df.columns else [],
            "bb_lower": clean_data(chart_df['BB_Lower'].tolist()) if 'BB_Lower' in chart_df.columns else [],
            "macd": clean_data(chart_df['MACD'].tolist()) if 'MACD' in chart_df.columns else [],
            "macd_signal": clean_data(chart_df['MACD_Signal'].tolist()) if 'MACD_Signal' in chart_df.columns else [],
            "macd_histogram": clean_data(chart_df['MACD_Histogram'].tolist()) if 'MACD_Histogram' in chart_df.columns else [],
            "rsi": clean_data(chart_df['RSI'].tolist()) if 'RSI' in chart_df.columns else [],
            "volume": clean_data(chart_df['Volume'].tolist()) if 'Volume' in chart_df.columns else [],
            "stoch_k": clean_data(chart_df['Stoch_K'].tolist()) if 'Stoch_K' in chart_df.columns else [],
            "stoch_d": clean_data(chart_df['Stoch_D'].tolist()) if 'Stoch_D' in chart_df.columns else [],
        }
        
        # 5. Get latest indicator values
        latest = df.iloc[-1]
        indicators = {
            "rsi": round(float(latest['RSI']), 2) if pd.notna(latest.get('RSI')) else None,
            "macd": round(float(latest['MACD']), 4) if pd.notna(latest.get('MACD')) else None,
            "macd_signal": round(float(latest['MACD_Signal']), 4) if pd.notna(latest.get('MACD_Signal')) else None,
            "sma_20": round(float(latest['SMA_20']), 2) if pd.notna(latest.get('SMA_20')) else None,
            "sma_50": round(float(latest['SMA_50']), 2) if pd.notna(latest.get('SMA_50')) else None,
            "bb_upper": round(float(latest['BB_Upper']), 2) if pd.notna(latest.get('BB_Upper')) else None,
            "bb_lower": round(float(latest['BB_Lower']), 2) if pd.notna(latest.get('BB_Lower')) else None,
            "atr": round(float(latest['ATR']), 2) if pd.notna(latest.get('ATR')) else None,
            "adx": round(float(latest['ADX']), 2) if pd.notna(latest.get('ADX')) else None,
            "stoch_k": round(float(latest['Stoch_K']), 2) if pd.notna(latest.get('Stoch_K')) else None,
            "stoch_d": round(float(latest['Stoch_D']), 2) if pd.notna(latest.get('Stoch_D')) else None,
            "vwap": round(float(latest['VWAP']), 2) if pd.notna(latest.get('VWAP')) else None,
            "support": round(float(latest['Support_1']), 2) if pd.notna(latest.get('Support_1')) else None,
            "resistance": round(float(latest['Resistance_1']), 2) if pd.notna(latest.get('Resistance_1')) else None,
        }

        # 6. Save to history
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "price": float(chart_df['Close'].iloc[-1]),
            "signal": signal_data,
            "indicators": indicators
        }
        history.append(history_entry)
        if len(history) > 50:
            history.pop(0)

        # 7. Check alerts
        triggered_alerts = []
        current_price = float(chart_df['Close'].iloc[-1])
        for alert in alerts:
            if alert['symbol'] == symbol:
                if alert['type'] == 'above' and current_price >= alert['price']:
                    triggered_alerts.append(alert)
                elif alert['type'] == 'below' and current_price <= alert['price']:
                    triggered_alerts.append(alert)

        return jsonify({
            "signal": signal_data,
            "market_data": chart_data,
            "indicators": indicators,
            "symbol": symbol,
            "current_price": current_price,
            "triggered_alerts": triggered_alerts
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict')
def predict():
    """AI Market Prediction with future price targets."""
    try:
        symbol = request.args.get('symbol', bot.SYMBOL)
        prediction = bot.get_market_prediction(symbol)
        
        if "error" in prediction:
            return jsonify(prediction), 500
        
        return jsonify(prediction)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/screener')
def screener():
    """Stock screener with customizable criteria."""
    try:
        criteria = request.args.get('criteria', 'momentum')
        results = bot.screen_stocks(criteria)
        return jsonify(results)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/sectors')
def sectors():
    """Sector performance analysis."""
    try:
        data = bot.get_sector_performance()
        return jsonify(data)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/indices')
def indices():
    try:
        data = bot.fetch_market_indices()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Portfolio Management
@app.route('/api/portfolio', methods=['GET', 'POST', 'DELETE'])
def manage_portfolio():
    global portfolio
    
    if request.method == 'GET':
        return jsonify(portfolio)
    
    elif request.method == 'POST':
        data = request.json
        portfolio.append({
            "id": len(portfolio) + 1,
            "symbol": data['symbol'],
            "quantity": data['quantity'],
            "buy_price": data['buy_price'],
            "date_added": datetime.now().isoformat()
        })
        return jsonify({"success": True, "portfolio": portfolio})
    
    elif request.method == 'DELETE':
        item_id = request.args.get('id', type=int)
        portfolio = [p for p in portfolio if p['id'] != item_id]
        return jsonify({"success": True, "portfolio": portfolio})

# Price Alerts
@app.route('/api/alerts', methods=['GET', 'POST', 'DELETE'])
def manage_alerts():
    global alerts
    
    if request.method == 'GET':
        return jsonify(alerts)
    
    elif request.method == 'POST':
        data = request.json
        alerts.append({
            "id": len(alerts) + 1,
            "symbol": data['symbol'],
            "price": data['price'],
            "type": data['type'],
            "created": datetime.now().isoformat()
        })
        return jsonify({"success": True, "alerts": alerts})
    
    elif request.method == 'DELETE':
        alert_id = request.args.get('id', type=int)
        alerts = [a for a in alerts if a['id'] != alert_id]
        return jsonify({"success": True, "alerts": alerts})

# Historical Data
@app.route('/api/history')
def get_history():
    return jsonify(history)

# Export Data
@app.route('/api/export/<format>')
def export_data(format):
    try:
        if format == 'json':
            data = {
                "portfolio": portfolio,
                "alerts": alerts,
                "history": history
            }
            return jsonify(data)
        
        elif format == 'csv':
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=['timestamp', 'symbol', 'price', 'action', 'confidence'])
            writer.writeheader()
            
            for entry in history:
                writer.writerow({
                    'timestamp': entry['timestamp'],
                    'symbol': entry['symbol'],
                    'price': entry['price'],
                    'action': entry['signal']['action'],
                    'confidence': entry['signal']['confidence']
                })
            
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'trading_history_{datetime.now().strftime("%Y%m%d")}.csv'
            )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
