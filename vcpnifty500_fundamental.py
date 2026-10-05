import requests
from vcpnifty500_ml import run_technical_vcp_filters

TELEGRAM_BOT_TOKEN = "8771040771:AAGpHJgC255W-RQW4uiijo-26z07Mvnk2qQ"
TELEGRAM_CHAT_ID = "5571350680"


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
        "📊 *Nifty 500 VCP Scan Report*\nಇಂದಿನ ಸ್ಕ್ಯಾನಿಂಗ್‌ನಲ್ಲಿ ಯಾವುದೇ"
        " ಸ್ಟಾಕ್‌ಗಳು ಮಾಸ್ಟರ್ ಫಿಲ್ಟರ್‌ಗಳನ್ನು ಪಾಸ್ ಮಾಡಿಲ್ಲ."
    )
  else:
    send_telegram_message(
        f"🚀 *Nifty 500 VCP Scan Report*\nಒಟ್ಟು {len(shortlisted_stocks)}"
        " ಸ್ಟಾಕ್‌ಗಳು ಸೆಲೆಕ್ಟ್ ಆಗಿವೆ!"
    )
    for stock in shortlisted_stocks:
      msg = (
          f"🔹 *Stock:* {stock['symbol']}\n💰 *Price:* ₹{stock['price']}\n📊"
          f" *RVOL:* {stock['rvol']}\n📈 *RSI:* {stock['rsi']}\n🏢 *Market"
          f" Cap:* ₹{stock['market_cap']} Cr"
      )
      send_telegram_message(msg)
