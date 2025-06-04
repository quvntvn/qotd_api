import os, requests, datetime, json

FIREBASE_API_KEY = os.environ["FCM_SERVER_KEY"]
DEVICE_TOPIC = "qotd"          # Ou token individuel
API_URL = os.environ["QOTD_URL"] + "/api/daily_quote"

quote = requests.get(API_URL, timeout=10).json()["citation"]

data = {
    "to": f"/topics/{DEVICE_TOPIC}",
    "notification": {
        "title": "Citation du jour",
        "body": quote
    }
}
requests.post(
    "https://fcm.googleapis.com/fcm/send",
    headers={"Authorization": f"key={FIREBASE_API_KEY}",
             "Content-Type": "application/json"},
    data=json.dumps(data),
    timeout=10
)
