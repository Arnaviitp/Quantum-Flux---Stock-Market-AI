# 🚀 Quick Start Guide - Quantum Flux AI

Welcome to your enhanced trading bot! This guide will help you get started with all the new features.

## ✅ Step 1: Verify Security

Your API key is now protected:
- ✅ Located in `.env` file
- ✅ `.gitignore` prevents accidental commits
- ✅ Never share your `.env` file!

## 🎮 Step 2: Explore the Interface

### Main Navigation
The app now has **4 main tabs**:

1. **📊 Analysis** - Market analysis and AI signals
2. **💼 Portrait** - Track your stock holdings
3. **🔔 Alerts** - Price alerts and notifications
4. **📈 History** - Past analyses and signals

### Header Controls
Look at the top right:
- **🌙 Theme Toggle** - Switch between dark/light modes
- **⏸️ Auto-Refresh** - Enable automatic updates (30s interval)
- **System Ready** - Status indicator

## 🎯 Step 3: Try Each Feature

### 1️⃣ Market Analysis (Original + Enhanced)
1. Select a stock from the dropdown
2. Click **Analyze Market**
3. View:
   - Current price
   - AI signal (BUY/SELL/HOLD)
   - Confidence level
   - Price chart
   - AI reasoning

**NEW**: Auto-refresh option for continuous monitoring!

### 2️⃣ Portfolio Management
1. Click the **💼 Portfolio** tab
2. Enter stock details:
   - Symbol: `RELIANCE.NS`
   - Quantity: `10`
   - Buy Price: `2500.00`
3. Click **Add to Portfolio**
4. View your holdings summary
5. Delete items with 🗑️ button

### 3️⃣ Price Alerts
1. Click the **🔔 Alerts** tab
2. Select a stock
3. Choose "Above" or "Below"
4. Enter target price
5. Click **Create Alert**
6. Get notified during analysis!

Example: Alert when RELIANCE.NS goes above ₹2800

### 4️⃣ View History
1. Click the **📈 History** tab
2. Browse all past analyses
3. See what AI recommended
4. Review confidence levels
5. Read AI reasoning for each

### 5️⃣ Auto-Refresh
1. Click **⏸️** button in header
2. It changes to **▶️**
3. Market analyzes every 30 seconds
4. Only works on Analysis tab
5. Click again to stop

### 6️⃣ Change Theme
1. Click **🌙** button
2. Interface switches to light mode
3. Button shows **☀️**
4. Try both and pick your favorite!

### 7️⃣ Export Data
1. Go to Analysis tab
2. Click **📥 Export Data**
3. Choose format:
   - OK = CSV (for Excel)
   - Cancel = JSON (for developers)
4. File downloads automatically

## 💡 Pro Tips

### 🎯 Best Practices
- Set alerts for your target buy/sell prices
- Check history before making decisions
- Use auto-refresh during active trading hours
- Export data regularly as backup
- Switch to light theme in bright environments

### ⚡ Shortcuts
- **Tabs**: Navigate with keyboard arrow keys (when focused)
- **Refresh**: F5 to reload entire page
- **Notifications**: Auto-dismiss after 3 seconds

### 🔍 Understanding Signals

**BUY (Green)** 🟢
- AI recommends buying
- Look for high confidence (>70%)
- Review reasoning carefully

**SELL (Red)** 🔴
- AI recommends selling
- Consider current holdings
- Don't panic-sell on low confidence

**HOLD (Yellow)** 🟡
- Market unclear or sideways
- Wait for better opportunity
- Good time to research

## 🎨 UI Elements Guide

### Color Coding
- **Cyan (#00f3ff)**: Primary accents, active states
- **Purple (#bf00ff)**: Secondary accents, SMA line
- **Green (#00ff9d)**: Success, BUY signals, positive changes
- **Red (#ff0055)**: Danger, SELL signals, negative changes
- **Yellow (#ffcc00)**: Warning, HOLD signals

### Notifications
- **Success**: Green glow (action completed)
- **Error**: Red glow (something wrong)
- **Warning**: Yellow glow (alerts triggered)
- **Info**: Cyan glow (general information)

## 📱 Mobile Usage

The app is fully responsive:
- Forms stack vertically on mobile
- Tabs scroll horizontally
- Touch-friendly buttons
- Optimized for small screens

## ⚠️ Important Notes

### Data Persistence
⚠️ **Current Version**: Data is stored in memory
- Portfolio, alerts, and history reset on server restart
- Export your data regularly!
- **Future**: Will use database for persistence

### API Limits
- Be mindful of GROQ API rate limits
- Don't spam the Analyze button
- Auto-refresh is optimized for 30s intervals

### Market Data
- Data from Yahoo Finance (yfinance)
- Some stocks may have delayed data
- Hourly candles may not be available for all stocks
- Falls back to daily data when needed

## 🆘 Troubleshooting

### Server won't start
```bash
# Check if .env file exists and has API key
cat .env  # Mac/Linux
type .env  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

###  No data showing
- Check internet connection
- Verify stock symbol is correct
- Try with RELIANCE.NS (reliable)

### Alerts not triggering
- Alerts only check during analysis
- Must analyze the specific stock
- Auto-refresh helps catch alerts

### Export not working
- Make sure you have analysis history
- Run at least one analysis first
- Check browser download settings

## 🎓 Learning Resources

### Understanding Technical Indicators
- **SMA (Simple Moving Average)**: Average price over 20 periods
  - Price > SMA = Potential uptrend
  - Price < SMA = Potential downtrend
  
- **RSI (Relative Strength Index)**: Momentum indicator (0-100)
  - > 70 = Overbought (may reverse down)
  - < 30 = Oversold (may reverse up)

### AI Confidence Levels
- **90-100%**: Very strong conviction
- **70-89%**: Strong signal
- **50-69%**: Moderate signal
- **< 50%**: Weak signal, low confidence

## 🔐 Security Checklist

Before sharing or deploying:
- [ ] `.env` file is in `.gitignore`
- [ ] No API keys in source code
- [ ] `.gitignore` is committed to repo
- [ ] README warns about `.env`
- [ ] Environment variables documented

## 📞 Next Steps

1. **Try all features**: Spend time exploring each tab
2. **Add some holdings**: Build a test portfolio
3. **Set alerts**: Practice with price alerts
4. **Enable auto-refresh**: Watch it work in real-time
5. **Export data**: Test the export functionality
6. **Read the full README**: Understand all capabilities

## 🎉 Congratulations!

You now have a fully-featured trading bot with:
- ✅ Protected API keys
- ✅ Portfolio tracking
- ✅ Price alerts
- ✅ Historical data
- ✅ Auto-refresh
- ✅ Theme options
- ✅ Data export
- ✅ Modern UI

**Happy Trading! 📈**

---

*Need help? Check the main README.md or review FEATURE_SUMMARY.md for detailed documentation.*
