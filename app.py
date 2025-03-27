from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Configuraciones
ULTRAMSG_TOKEN = "r4wm825i3lqivpku"
ULTRAMSG_INSTANCE_ID = "instance111839"
ULTRAMSG_URL = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"

REDGPS_API_URL = "https://redgps-proxy.onrender.com/activos"  # Proxy que genera token cada 6h


def consultar_bateria(placa):
    try:
        response = requests.get(REDGPS_API_URL)
        response.raise_for_status()
        unidades = response.json()

        for u in unidades:
            if u.get("name") == placa:
                return f"🔋 Batería de la unidad {placa}: {u.get('batteryLevel', 'N/A')}% (Reporte: {u.get('lastUpdate', 'N/A')})"
        return f"⚠️ No se encontró información para la unidad {placa}."

    except Exception as e:
        return f"❌ Error al consultar RedGPS: {e}"


def enviar_mensaje(numero, mensaje):
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": numero,
        "body": mensaje
    }
    requests.post(ULTRAMSG_URL, data=payload)


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    mensaje = data.get("body", "").strip()
    numero = data.get("from")

    print("Mensaje recibido:", mensaje)

    if mensaje.lower().startswith("bateria"):
        partes = mensaje.split()
        if len(partes) >= 2:
            placa = partes[1].strip()
            respuesta = consultar_bateria(placa)
        else:
            respuesta = "Por favor indica la placa. Ej: bateria CE-214700"
    else:
        respuesta = "Hola, soy Lía 🤖. Puedes preguntarme por la batería usando: bateria [PLACA]"

    enviar_mensaje(numero, respuesta)
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)



