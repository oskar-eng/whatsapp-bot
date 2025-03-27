from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Webhook recibido:", data)

    # Extraer mensaje
    try:
        message = data["body"].strip().lower()
        sender = data["from"]

        respuesta = ""
        if message == "hola":
            respuesta = "Hola! 😊 Soy Lia, tu asistente virtual. ¿En qué puedo ayudarte hoy?"
        elif message.startswith("bateria"):
            respuesta = "Para consultar la batería, por favor dime la placa. Ejemplo: bateria ABC123."
        else:
            respuesta = "Lo siento, no entendí tu mensaje. Puedes escribir 'hola' para comenzar."

        # Enviar respuesta a UltraMsg
        import requests
        ultramsg_url = f"https://api.ultramsg.com/instance{os.getenv('ULTRAMSG_INSTANCE_ID')}/messages/chat"
        payload = {
            "token": os.getenv("ULTRAMSG_TOKEN"),
            "to": sender,
            "body": respuesta
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        requests.post(ultramsg_url, data=payload, headers=headers)

    except Exception as e:
        print("Error procesando webhook:", e)

    return jsonify({"status": "ok"})


@app.route("/")
def home():
    return "Bot de WhatsApp corriendo con Lia 🤖"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
