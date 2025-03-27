# app.py
from flask import Flask, request
import requests

app = Flask(__name__)

# Configuración de UltraMsg
ULTRAMSG_INSTANCE_ID = "instance111839"
ULTRAMSG_TOKEN = "r4wm825i3lqivpku"

# URL de RedGPS-Proxy (ya gestiona el token)
REDGPS_PROXY_URL = "https://redgps-proxy.onrender.com/activos"


def obtener_dato_bateria(placa):
    try:
        response = requests.get(REDGPS_PROXY_URL)
        data = response.json()

        for unidad in data:
            if unidad.get("unidad", "").lower() == placa.lower():
                return unidad.get("bateria")

        return None
    except Exception as e:
        print("Error al consultar RedGPS:", e)
        return None


def enviar_mensaje(numero, mensaje):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": numero,
        "body": mensaje
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Error al enviar mensaje:", e)


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    mensaje = data.get("body", "").strip().lower()
    numero = data.get("from", "")

    if mensaje.startswith("bateria"):
        partes = mensaje.split()
        if len(partes) >= 2:
            placa = " ".join(partes[1:]).strip()
            bateria = obtener_dato_bateria(placa)

            if bateria is not None:
                enviar_mensaje(numero, f"La unidad {placa} tiene {bateria}% de batería")
            else:
                enviar_mensaje(numero, f"No se encontró información para la unidad {placa}")
        else:
            enviar_mensaje(numero, "Envía: bateria [placa de unidad]")
    else:
        enviar_mensaje(numero, "Hola, soy Lía 🧙‍♀️. Puedes consultar la batería así: bateria [placa]")

    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


