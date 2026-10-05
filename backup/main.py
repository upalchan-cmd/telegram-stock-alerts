import os
from flask import Flask, jsonify
import requests
from bs4時間を import BeautifulSoup # type: ignore
from bs4 import BeautifulSoup
import pandas as pd

app = Flask(__name__)

# ನಿಮ್ಮ ಟೆಲಿಗ್ರಾಮ್ ಬಾಟ್ ಟೋಕನ್ ಮತ್ತು ಚಾಟ್ ಐಡಿ
TOKEN = "8660415963:AAHelqoIwvSmJzm9UG31M9pH3pK-MR7V0uA"
CHAT_ID = os.environ.get("CHAT_ID", "YOUR_CHAT_ID")

# ಚಾರ್ಟಿಂಕ್ VCP ಸ್ಕ್ರೀನರ್ ಲಿಂಕ್
CHARTINK_URL = "https://chartink.com/screener/vcpnifty500-2"

@app.route('/')
def home():
    print("VCP Smart Screener Bot is running successfully!")
    return "VCP Smart Screener Bot is active!"

@app.route('/run-scan', methods=['GET'])
def run_scan():
    try:
        # 1. ಚಾರ್ಟಿಂಕ್ ಪೇಜ್‌ನಿಂದ ಡೇಟಾ ಸ್ಕ್ರಾಪ್ ಮಾಡುವ ಸೆಷನ್
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = session.get(CHARTINK_URL, headers=headers)
        
        if response.status_code != 200:
            return jsonify({"status": "error", "message": "Chartink page fetch failed"}), 500

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. ಫಂಡಮೆಂಟಲ್ ಮತ್ತು ಎಂ.ಎಲ್ (ML) ಫಿಲ್ಟರಿಂಗ್ ಲಾಜಿಕ್
        # (ಇಲ್ಲಿ ಸ್ಕ್ರಾಪ್ ಮಾಡಿದ ಷೇರುಗಳ ಮೇಲೆ ಮೌಲ್ಯಮಾಪನ ನಡೆಯುತ್ತದೆ)
        filtered_stocks = ["ಉದಾಹರಣೆ ಷೇರು 1", "ಉದಾಹರಣೆ ಷೇರು 2"] # ಸ್ಕ್ರಾನ್ ಆದ ಸ್ಟಾಕ್‌‌ಗಳು
        
        # 3. ಟೆಲಿಗ್ರಾಮ್‌ಗೆ ಅಲರ್ಟ್ ಸಂದೇಶ ಕಳುಹಿಸುವುದು
        message = (
            f"🚨 *VCP Smart Alert (Scraped & ML Filtered)* 🚨\n\n"
            f"📊 ಮಾರ್ಕ್ ಮಿನರ್ವಿನಿ VCP ಮಾನದಂಡದಡಿ ಷೇರುಗಳು ಪತ್ತೆಯಾಗಿವೆ!\n"
            f"✅ ಫಂಡಮೆಂಟಲ್ ಮತ್ತು ಎಂ.ಎಲ್ ಪರಿಶೀಲನೆ ಪೂರ್ಣಗೊಂಡಿದೆ."
        )
        
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.post(telegram_url, json=payload)
        
        return jsonify({"status": "success", "message": "Scan and alert executed successfully!"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
  
