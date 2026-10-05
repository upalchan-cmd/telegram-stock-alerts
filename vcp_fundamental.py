import os
import re
import requests
import yfinance as yf
from bs4 import BeautifulSoup

try:
  import cloudscraper

  HAS_CLOUDSCRAPER = True
except ImportError:
  HAS_CLOUDSCRAPER = False

SCREENER_USER = "upalchan84@gmail.com"
SCREENER_PASS = "bmc50622"


def get_vcp_and_fundamentals(symbol):
  clean_sym = symbol.replace(".NS", "").replace(".BO", "").strip().upper()
  data = {
      "symbol": clean_sym,
      "current_price": None,
      "sma_50": None,
      "sma_150": None,
      "sma_200": None,
      "high_52w": None,
      "low_52w": None,
      "vcp_passed": False,
      "roce": None,
      "roe": None,
      "debt_to_equity": None,
  }

  try:
    ticker = yf.Ticker(f"{clean_sym}.NS")
    hist = ticker.history(period="1y")
    info = ticker.info or {}

    if not hist.empty:
      curr_price = hist["Close"].iloc[-1]
      data["current_price"] = curr_price
      data["high_52w"] = hist["High"].max()
      data["low_52w"] = hist["Low"].min()

      # Minervini Trend Template Moving Averages
      data["sma_50"] = hist["Close"].rolling(window=50).mean().iloc[-1]
      data["sma_150"] = hist["Close"].rolling(window=150).mean().iloc[-1]
      data["sma_200"] = hist["Close"].rolling(window=200).mean().iloc[-1]

      # Minervini VCP / Trend Template Basic Checks:
      # 1. Price above 150 & 200 SMA
      # 2. Price is at least 25% above 52w low
      # 3. Price is within 25% of 52w high
      cond_1 = (
          curr_price > data["sma_150"] and curr_price > data["sma_200"]
          if data["sma_200"]
          else False
      )
      cond_2 = (
          curr_price >= data["low_52w"] * 1.25 if data["low_52w"] else False
      )
      cond_3 = (
          curr_price >= data["high_52w"] * 0.75 if data["high_52w"] else False
      )

      if cond_1 and cond_2 and cond_3:
        data["vcp_passed"] = True

    if info:
      if info.get("returnOnEquity") is not None:
        data["roe"] = round(info.get("returnOnEquity") * 100.0, 1)
      if info.get("debtToEquity") is not None:
        data["debt_to_equity"] = round(info.get("debtToEquity") / 100.0, 2)

  except Exception as e:
    print(f"Error fetching data for {clean_sym}: {e}")

  return data
