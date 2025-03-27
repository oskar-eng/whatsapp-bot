from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Configura tu token y API URL de UltraMsg aquí
ULTRAMSG_INSTANCE_ID = "instance111839"  # reemplaza con tu instancia
ULTRAMSG_TOKEN = "r4wm825i3qlivpku"  # reemplaza con tu token
ULTRAMSG_URL = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"

# Configura tu endpoint del proxy RedGPS (donde se genera el token dinámico)
REDGPS_PROXY = "https://redgps-proxy.onrender.com/activos"

@app.route("/", methods=["GET"])
def index():
    return "🟢 Bot de WhatsApp activo!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 Mensaje recibido:", data)

    if not data:
        return "No data", 400

    message = data.get("body", "").strip().lower()
    sender = data.get("from")

    if not message or not sender:
        return "Missing data", 400

    response_text = ""

    if message == "hola":
        response_text = "Hola, soy Lía 🤖. ¿Cómo puedo ayudarte?"

    elif message.startswith("bateria"):
        partes = message.split(" ")
        if len(partes) >= 2:
            placa = partes[1].upper()
            response_text = obtener_bateria(placa)
        else:
            response_text = "Por favor envía: bateria [placa]"

    if response_text:
        enviar_whatsapp(sender, response_text)

    return jsonify({"status": "ok"})

def obtener_bateria(placa):
    try:
        res = requests.get(REDGPS_PROXY)
        unidades = res.json()
        for u in unidades:
            if u.get("UnitPlate", "").upper() == placa:
                bateria = u.get("BateriaGps", "?")
                fecha = u.get("ReportDate", "sin fecha")
                return f"🔋 Batería: {bateria}%\n⏰ Último reporte: {fecha}"
        return f"❌ No encontré información para la placa {placa}"
    except Exception as e:
        print("Error al consultar el proxy RedGPS:", e)
        return "Error al obtener la información de RedGPS."

def enviar_whatsapp(to_number, text):
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": to_number,
        "body": text
    }
    try:
        res = requests.post(ULTRAMSG_URL, data=payload)
        print("✉️ Mensaje enviado:", res.text)
    except Exception as e:
        print("Error al enviar mensaje:", e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

