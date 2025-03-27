# app.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Token e instancia de UltraMsg
ULTRAMSG_INSTANCE_ID = "111839"  # remplaza si usas otra
ULTRAMSG_TOKEN = "r4wm825i3lqivpku"

# URL del bot de RedGPS que devuelve todos los activos
REDGPS_API_URL = "https://redgps-proxy.onrender.com/activos"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Webhook recibido:", data)

    if not data or "body" not in data or "from" not in data:
        return jsonify({"error": "Invalid payload"}), 400

    message = data["body"].strip().lower()
    phone = data["from"].replace("@c.us", "")

    if message.startswith("bateria"):
        partes = message.split()
        if len(partes) == 2:
            placa = partes[1].upper()
            return responder_bateria(phone, placa)
        else:
            return enviar_mensaje(phone, "Formato incorrecto. Usa: bateria [placa]")

    elif message in ["hola", "lia", "buenas"]:
        return enviar_mensaje(phone, "Hola, soy Lía 🤖. ¡¿Cómo puedo ayudarte?!")

    return jsonify({"status": "ignorado"}), 200

def responder_bateria(telefono, placa):
    try:
        response = requests.get(REDGPS_API_URL)
        unidades = response.json()

        for unidad in unidades:
            if unidad.get("UnitPlate", "").upper() == placa:
                bateria = unidad.get("BateriaGps", "N/A")
                fecha = unidad.get("ReportDate", "Sin fecha")
                mensaje = f"🔋 Batería GPS: {bateria}%\n📅 Último reporte: {fecha}"
                return enviar_mensaje(telefono, mensaje)

        return enviar_mensaje(telefono, f"No encontré la placa {placa} en RedGPS")

    except Exception as e:
        print("Error al consultar RedGPS:", e)
        return enviar_mensaje(telefono, "Error consultando RedGPS. Intenta nuevamente.")

def enviar_mensaje(telefono, texto):
    url = f"https://api.ultramsg.com/instance{ULTRAMSG_INSTANCE_ID}/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": telefono,
        "body": texto
    }
    r = requests.post(url, data=payload)
    print("Respuesta de UltraMsg:", r.text)
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)



