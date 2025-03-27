from flask import Flask, request
import requests
import json

app = Flask(__name__)

ULTRAMSG_API_URL = "https://api.ultramsg.com/instance111839/messages/chat"
ULTRAMSG_TOKEN = "r4wm825i3lqivpku"

REDGPS_API_URL = "https://redgps-proxy.onrender.com/activos"


def get_redgps_data(plate):
    try:
        response = requests.get(REDGPS_API_URL)
        data = response.json()

        for unit in data:
            if unit.get("UnitPlate", "").lower() == plate.lower():
                return {
                    "placa": unit.get("UnitPlate"),
                    "bateria_gps": unit.get("BateriaGps"),
                    "ultimo_reporte": unit.get("ReportDate"),
                }
    except Exception as e:
        print("Error al obtener datos de RedGPS:", e)
    return None


def send_whatsapp_message(to, message):
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": to,
        "body": message
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    requests.post(ULTRAMSG_API_URL, data=payload, headers=headers)


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return "No data", 400

    mensaje = data.get("body", "").strip()
    numero = data.get("from")

    if mensaje.lower().startswith("bateria"):
        partes = mensaje.split()
        if len(partes) > 1:
            placa = partes[1]
            info = get_redgps_data(placa)

            if info:
                texto = f"🚗 Unidad: {info['placa']}\n🔋 Batería GPS: {info['bateria_gps']}%\n📅 Último reporte: {info['ultimo_reporte']}"
            else:
                texto = "No se encontró información para esa placa."
        else:
            texto = "Por favor, indica la placa. Ejemplo: bateria ABC123"
        send_whatsapp_message(numero, texto)

    elif mensaje.lower() in ["hola", "buenas", "lia"]:
        send_whatsapp_message(numero, "Hola, soy Lía 🧙‍♂️. Puedes consultarme la batería de una unidad escribiendo: bateria [placa]")

    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)




