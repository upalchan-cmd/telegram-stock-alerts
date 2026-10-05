import requests
from vcpnifty500_ml import run_technical_vcp_filters

TELEGRAM_BOT_TOKEN = "8771040771:AAGpHJgC255W-RQW4uiijo-26z07Mvnk2qQ"
TELEGRAM_CHAT_ID = (
    "YOUR_CHAT_ID_HERE"  # ನಿಮ್ಮ ಟೆಲಿಗ್ರಾಮ್ ಚಾಟ್ ಐಡಿಯನ್ನು ಇಲ್ಲಿ ಹಾಕಿ
)


def send_telegram_message(message):
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload, timeout=10)
  except Exception as e:
    print(f"Telegram Error: {e}")


if __name__ == "__main__":
  print("Scanning entire Nifty 500 stocks with Master VCP Filters...")
  shortlisted_stocks = run_technical_vcp_filters()

  if not shortlisted_stocks:
    print("No stocks matched the master technical filters today.")
    send_telegram_message(
        "📊 *Nifty 500 VCP Scan:* No stocks matched the filters today."
    )
  else:
    for stock in shortlisted_stocks:
      msg = (
          f"🚀 *Nifty 500 VCP Master Alert*\n"
          f"🔹 *Stock:* {stock['symbol']}\n"
          f"💰 *Price:* ₹{stock['price']}\n"
          f"📊 *RVOL:* {stock['rvol']}\n"
          f"📈 *RSI:* {stock['rsi']}\n"
          f"🏢 *Market Cap:* ₹{stock['market_cap']} Cr\n"
          f"Status: Technical & VCP Setup Passed!"
      )
      print(msg)
      send_telegram_message(msg)
