from flask import Flask, request
import requests
import os

app = Flask(__name__)

ULTRAMSG_INSTANCE_ID = "instance111839"
ULTRAMSG_TOKEN = "r4wm825i3lqivpku"
REDGPS_PROXY_URL = "https://redgps-proxy.onrender.com/activos"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return {"status": "no data"}, 400

    try:
        message = data.get("body", "").strip().lower()
        sender = data.get("from")

        if message.startswith("bateria"):
            parts = message.split()
            if len(parts) == 2:
                placa = parts[1].upper()
                info = get_battery_info(placa)
                send_message(sender, info)
            else:
                send_message(sender, "Formato incorrecto. Usa: bateria [placa]")
        else:
            send_message(sender, "Hola, soy Lía 🤖. Escribe 'bateria [placa]' para conocer el estado de batería.")

    except Exception as e:
        print("Error:", str(e))

    return {"status": "ok"}, 200

def get_battery_info(placa):
    try:
        response = requests.get(REDGPS_PROXY_URL)
        data = response.json()

        for unidad in data:
            if unidad.get("unidad") == placa:
                return f"🔋 Batería: {unidad['bateria']}%\nIMEI: {unidad['imei']}\n📅 Último reporte: {unidad['ultimo_reporte']}"

        return "Unidad no encontrada. Verifica la placa."
    except Exception as e:
        return f"Error al consultar datos: {str(e)}"

def send_message(to, message):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": to,
        "body": message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Error al enviar mensaje:", str(e))

if __name__ == "__main__":
    app.run(debug=True, port=10000)


