from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Mensaje recibido:", data)  # Para debug en logs de Render

    try:
        mensaje = data["data"]["body"].strip().lower()
        telefono = data["data"]["from"]

        if "hola" in mensaje:
            enviar_mensaje(telefono, "Hola, soy Lía 🤖. ¿Cómo puedo ayudarte?")

    except Exception as e:
        print("Error procesando mensaje:", str(e))

    return jsonify({"status": "ok"})


def enviar_mensaje(telefono, mensaje):
    url = "https://api.ultramsg.com/instance111839/messages/chat"
    payload = {
        "token": "r4wm825i3lqivpku",
        "to": telefono,
        "body": mensaje
    }
    response = requests.post(url, data=payload)
    print("Respuesta del envío:", response.text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

