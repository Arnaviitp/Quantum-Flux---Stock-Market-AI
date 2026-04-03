import yfinance as yf

symbols = ["RELIANCE.NS", "TATAMOTORS.NS"]
for symbol in symbols:
    print(f"\nTesting {symbol}...")
    try:
        # Try 1h first
        print("  Attempting 1h interval...")
        df = yf.download(symbol, period="5d", interval="1h", progress=False)
        print(f"  1h Shape: {df.shape}")
        
        if df.empty:
            # Try 1d if 1h fails
            print("  1h failed/empty. Attempting 1d interval...")
            df = yf.download(symbol, period="1mo", interval="1d", progress=False)
            print(f"  1d Shape: {df.shape}")

    except Exception as e:
        print(f"  Error: {e}")
