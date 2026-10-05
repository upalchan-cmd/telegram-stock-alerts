import numpy as np
import pandas as pd
import requests
import yfinance as yf


def get_entire_nifty500_symbols():
  """ಎಂಟೈರ್ ನಿಫ್ಟಿ 500 ಸ್ಟಾಕ್ ಸಿಂಬಲ್‌ಗಳನ್ನು ನೇರವಾಗಿ NSE/GitHub ನಿಂದ ಪಡೆಯುತ್ತದೆ"""
  url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/122.0.0.0 Safari/537.36"
      )
  }
  try:
    res = requests.get(url, headers=headers, timeout=10)
    if res.status_code == 200:
      from io import StringIO

      df = pd.read_csv(StringIO(res.text))
      symbols = df["Symbol"].dropna().tolist()
      # ಯಾಹೂ ಫೈನಾನ್ಸ್‌ಗೆ ತಕ್ಕಂತೆ .NS ಸೇರಿಸುವುದು
      return [f"{sym.strip()}.NS" for sym in symbols]
  except Exception as e:
    print(f"Error fetching Nifty 500 list: {e}")

  # ಫಾಲ್ಬೆಕ್ ಆಗಿ ವಿಕಿಪೀಡಿಯಾ ಅಥವಾ ಬೇರೆ ಮೂಲದಿಂದ ಪಡೆಯಲು
  try:
    wiki_url = (
        "https://en.wikipedia.org/wiki/NIFTY_500"  # ಉದಾಹರಣೆ ಫಾಲ್ಬೆಕ್ ಲಿಂಕ್
    )
    tables = pd.read_html(wiki_url)
    for table in tables:
      if "Symbol" in table.columns:
        symbols = table["Symbol"].dropna().tolist()
        return [f"{str(sym).strip()}.NS" for sym in symbols]
  except Exception:
    pass

  return []


def run_technical_vcp_filters():
  symbols = get_entire_nifty500_symbols()
  print(f"Total Nifty 500 stocks loaded: {len(symbols)}")
  filtered_stocks = []

  for sym in symbols:
    try:
      ticker = yf.Ticker(sym)
      hist = ticker.history(period="6mo")
      info = ticker.info or {}

      if hist.empty or len(hist) < 200:
        continue

      # 4. ಮಾರ್ಕೆಟ್ ಕ್ಯಾಪ್ (ಕನಿಷ್ಠ ₹5,000 ಕೋಟಿ)
      mcap = info.get("marketCap", 0)
      market_cap_cr = mcap / 10000000.0 if mcap else 0
      if market_cap_cr < 5000:
        continue

      close = hist["Close"]
      volume = hist["Volume"]

      # 2 & 3. ಮೂವಿಂಗ್ ಆವರೇಜಸ್ (20, 50, 200 EMA) ಮತ್ತು ಪ್ರೈಸ್ ಟ್ರೆಂಡ್
      ema_20 = close.ewm(span=20, adjust=False).mean().iloc[-1]
      ema_50 = close.ewm(span=50, adjust=False).mean().iloc[-1]
      ema_200 = close.ewm(span=200, adjust=False).mean().iloc[-1]
      curr_price = close.iloc[-1]

      # ಬುಲಿಶ್ ಟ್ರೆಂಡ್ ಮತ್ತು ಕ್ರಮಬದ್ಧ ಜೋಡಣೆ (Price > 20 EMA > 50 EMA > 200 EMA)
      if not (
          curr_price > ema_20
          and ema_20 > ema_50
          and ema_50 > ema_200
          and curr_price > ema_200
      ):
        continue

      # 1. RVOL (Relative Volume > 1.5)
      avg_vol_20 = volume.rolling(window=20).mean().iloc[-1]
      rvol = volume.iloc[-1] / avg_vol_20 if avg_vol_20 > 0 else 0
      if rvol < 1.5:
        continue

      # 5. RSI (55 ರಿಂದ 72 ರವರೆಗೆ)
      delta = close.diff()
      gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
      loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
      rs = gain / loss
      rsi = 100 - (100 / (1 + rs))
      curr_rsi = rsi.iloc[-1]
      if not (55 <= curr_rsi <= 72):
        continue

      # 6. ಕನಿಷ್ಠ ವಹಿವಾಟು ಮೌಲ್ಯ (Min Traded Value >= ₹1,00,000)
      traded_value = curr_price * volume.iloc[-1]
      if traded_value < 100000:
        continue

      clean_name = sym.replace(".NS", "")
      filtered_stocks.append({
          "symbol": clean_name,
          "price": round(curr_price, 2),
          "rvol": round(rvol, 2),
          "rsi": round(curr_rsi, 2),
          "market_cap": round(market_cap_cr, 2),
      })

    except Exception:
      continue

  return filtered_stocks

