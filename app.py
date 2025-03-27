from flask import Flask, request

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📥 Webhook recibido:", data)

    if data and "body" in data and "text" in data["body"]:
        mensaje = data["body"]["text"].strip().lower()
        numero = data["body"]["from"]

        if "hola" in mensaje:
            enviar_respuesta(numero, "Hola, ¿en qué puedo ayudarte?")
    
    return "OK", 200

# Función para enviar respuesta usando UltraMsg
import requests
def enviar_respuesta(numero, mensaje):
    url = "https://api.ultramsg.com/instance111839/messages/chat"
    payload = {
        "token": "r4wm825i3lqivpku",
        "to": numero,
        "body": mensaje
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)
    print("📤 Respuesta enviada:", response.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
