import requests
import sys

# Usage: python set_webhook.py <YOUR_RENDER_URL>
# Example: python set_webhook.py https://ondc-setu-api-xxxx.onrender.com

if len(sys.argv) < 2:
    print("Usage: python set_webhook.py <YOUR_RENDER_URL>")
    sys.exit(1)

BASE_URL = sys.argv[1].rstrip("/")
WEBHOOK_URL = f"{BASE_URL}/v1/telegram/webhook"
BOT_TOKEN = "8563653060:AAEJ8a9vQnoyXYNuxXV4NmMnyCjRh877ack" # Hardcoded for convenience

print(f"Setting webhook to: {WEBHOOK_URL}")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
resp = requests.post(url, data={"url": WEBHOOK_URL})

print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}")
