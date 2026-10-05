from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import pandas as pd
import requests
import yfinance as yf


def get_entire_nifty500_symbols():
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
      return [f"{sym.strip()}.NS" for sym in symbols]
  except Exception as e:
    print(f"Error fetching Nifty 500 list: {e}")

  try:
    wiki_url = "https://en.wikipedia.org/wiki/NIFTY_500"
    tables = pd.read_html(wiki_url)
    for table in tables:
      if "Symbol" in table.columns:
        symbols = table["Symbol"].dropna().tolist()
        return [f"{str(sym).strip()}.NS" for sym in symbols]
  except Exception:
    pass

  return []


def process_single_stock(sym):
  try:
    ticker = yf.Ticker(sym)
    hist = ticker.history(period="6mo")
    info = ticker.info or {}

    if hist.empty or len(hist) < 200:
      return None

    # 4. ಮಾರ್ಕೆಟ್ ಕ್ಯಾಪ್ (ಕನಿಷ್ಠ ₹5,000 ಕೋಟಿ)
    mcap = info.get("marketCap", 0)
    market_cap_cr = mcap / 10000000.0 if mcap else 0
    if market_cap_cr < 5000:
      return None

    close = hist["Close"]
    volume = hist["Volume"]

    # 2 & 3. ಮೂವಿಂಗ್ ಆವರೇಜಸ್ (20, 50, 200 EMA) ಮತ್ತು ಪ್ರೈಸ್ ಟ್ರೆಂಡ್
    ema_20 = close.ewm(span=20, adjust=False).mean().iloc[-1]
    ema_50 = close.ewm(span=50, adjust=False).mean().iloc[-1]
    ema_200 = close.ewm(span=200, adjust=False).mean().iloc[-1]
    curr_price = close.iloc[-1]

    # ಕ್ರಮಬದ್ಧ ಜೋಡಣೆ ಮತ್ತು ಬುಲಿಶ್ ಟ್ರೆಂಡ್
    if not (
        curr_price > ema_20
        and ema_20 > ema_50
        and ema_50 > ema_200
        and curr_price > ema_200
    ):
      return None

    # 1. RVOL (Relative Volume > 1.5)
    avg_vol_20 = volume.rolling(window=20).mean().iloc[-1]
    rvol = volume.iloc[-1] / avg_vol_20 if avg_vol_20 > 0 else 0
    if rvol < 1.5:
      return None

    # 5. RSI (55 ರಿಂದ 72 ರವರೆಗೆ)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    curr_rsi = rsi.iloc[-1]
    if not (55 <= curr_rsi <= 72):
      return None

    # 6. ಕನಿಷ್ಠ ವಹಿವಾಟು ಮೌಲ್ಯ (Min Traded Value >= ₹1,00,000)
    traded_value = curr_price * volume.iloc[-1]
    if traded_value < 100000:
      return None

    clean_name = sym.replace(".NS", "")
    return {
        "symbol": clean_name,
        "price": round(curr_price, 2),
        "rvol": round(rvol, 2),
        "rsi": round(curr_rsi, 2),
        "market_cap": round(market_cap_cr, 2),
    }

  except Exception:
    return None


def run_technical_vcp_filters():
  symbols = get_entire_nifty500_symbols()
  print(f"Total Nifty 500 stocks loaded: {len(symbols)}")
  filtered_stocks = []

  # Multi-threading ಬಳಸಿ ಒಂದೇ ಸಮಯದಲ್ಲಿ ಹಲವು ಸ್ಟಾಕ್‌ಗಳನ್ನು ಸ್ಕ್ಯಾನ್ ಮಾಡುವುದು
  with ThreadPoolExecutor(max_workers=20) as executor:
    futures = {
        executor.submit(process_single_stock, sym): sym for sym in symbols
    }
    for future in as_completed(futures):
      result = future.result()
      if result:
        filtered_stocks.append(result)

  return filtered_stocks
