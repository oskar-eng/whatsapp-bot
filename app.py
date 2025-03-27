from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configura tu instancia y token de UltraMsg
INSTANCE_ID = "instance111839"
TOKEN = "r4wm825i3lqivpku"
API_URL = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    message = data.get("body", "").strip().lower()
    sender = data.get("from", "")

    if message == "hola":
        payload = {
            "token": TOKEN,
            "to": sender,
            "body": "Hola 👋, soy Lía. ¡Estoy conectada y lista para ayudarte!"
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        requests.post(API_URL, data=payload, headers=headers)

    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

