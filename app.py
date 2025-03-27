from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Mensaje recibido:", data)

    if data and data.get("event_type") == "message_received":
        message = data.get("body", "").lower()
        sender = data.get("from", "")

        if "hola" in message:
            # Aqui llamamos a UltraMsg para responder (puedes cambiar el mensaje)
            import requests
            instance_id = "instance111839"  # <-- Tu ID
            token = "r4wm825i3lqivpku"        # <-- Tu token
            url = f"https://api.ultramsg.com/{instance_id}/messages/chat"

            payload = {
                "token": token,
                "to": sender,
                "body": "Hola, soy Lía y estoy conectada :)"
            }

            response = requests.post(url, data=payload)
            print("Respuesta de UltraMsg:", response.text)

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
