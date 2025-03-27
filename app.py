from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Variables de entorno o directamente en el código (reemplazar por los reales)
ULTRAMSG_INSTANCE_ID = "instance111839"
ULTRAMSG_TOKEN = "r4wm825i3lqivpku"
REDGPS_PROXY_URL = "https://redgps-proxy.onrender.com/activos"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    mensaje = data.get("body", "").strip().lower()
    telefono = data.get("from")

    if mensaje.startswith("bateria"):
        partes = mensaje.split()
        if len(partes) == 2:
            placa = partes[1].upper()
            activos = requests.get(REDGPS_PROXY_URL).json()

            for u in activos:
                if u.get("name", "").upper() == placa:
                    bateria = u.get("batteryLevel")
                    ultimo = u.get("lastUpdate")
                    respuesta = f"La unidad {placa} tiene {bateria}% de batería.\nÚltimo reporte: {ultimo}"
                    enviar_mensaje(telefono, respuesta)
                    break
            else:
                enviar_mensaje(telefono, f"No se encontró información para la unidad {placa}.")
        else:
            enviar_mensaje(telefono, "Formato incorrecto. Usa: bateria [placa]")
    else:
        enviar_mensaje(telefono, "Hola, soy Lía 🧙‍♀️. Escribe: bateria [placa] para consultar el estado de batería.")

    return {"success": True}, 200

def enviar_mensaje(telefono, mensaje):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": telefono,
        "body": mensaje
    }
    requests.post(url, data=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))




