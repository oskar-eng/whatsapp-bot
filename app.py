
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot de WhatsApp activo"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    message = data.get("body", "").lower()
    sender = data.get("from")

    respuesta = ""
    if "hola" in message:
        respuesta = "Hola, soy Lía 🤖. ¿Cómo puedo ayudarte?"
    elif "batería" in message and "placa" in message:
        respuesta = "Por favor, indícame la placa, por ejemplo: batería ABC123"
    elif "batería" in message:
        partes = message.split()
        if len(partes) == 2:
            placa = partes[1].upper()
            # Aquí iría la lógica para obtener los datos desde RedGPS
            respuesta = f"🔋 Batería de {placa}: 85%\n📍 Último reporte: 2025-03-27 10:41:42"
        else:
            respuesta = "Formato incorrecto. Usa: batería [placa]"
    else:
        respuesta = "No entendí tu mensaje. Escribe 'hola' o 'batería [placa]' para ayudarte."

    print(f"Responder a {sender}: {respuesta}")
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
