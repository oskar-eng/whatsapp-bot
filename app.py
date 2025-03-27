# app.py
from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Configuraciones de UltraMsg
ULTRAMSG_INSTANCE_ID = "instance111839"  # Cambia por tu ID
ULTRAMSG_TOKEN = "r4wm825i3lqivpku"      # Cambia por tu token
ULTRAMSG_URL = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"

# Endpoint para obtener el token actualizado desde el redgps-proxy
REDGPS_TOKEN_URL = "https://redgps-proxy.onrender.com/token"
REDGPS_DATA_URL = "https://api.service24gps.com/api/v1/getdata"
APIKEY_REDGPS = "c95d7f74eccb5702a620011f128f750e"  # Tu APIKEY


def obtener_token_redgps():
    try:
        r = requests.get(REDGPS_TOKEN_URL)
        return r.json().get("token")
    except Exception as e:
        print("Error al obtener token RedGPS:", e)
        return None


def obtener_bateria_por_placa(placa):
    token = obtener_token_redgps()
    if not token:
        return "No se pudo obtener token de RedGPS."

    payload = {
        "apikey": APIKEY_REDGPS,
        "token": token,
        "UseUTCDate": "0",
        "sensores": "1"
    }
    try:
        r = requests.post(REDGPS_DATA_URL, data=payload)
        unidades = r.json().get("data", [])
        for unidad in unidades:
            if unidad["UnitPlate"].lower() == placa.lower():
                return f'La unidad {placa.upper()} tiene {unidad["BatteryGps"]}% de batería. Último reporte: {unidad["ReportDate"]}'
        return f"No se encontró información para la unidad {placa.upper()}."
    except Exception as e:
        print("Error al consultar RedGPS:", e)
        return "Error al obtener información de RedGPS."


def enviar_mensaje(numero, mensaje):
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": numero,
        "body": mensaje
    }
    try:
        requests.post(ULTRAMSG_URL, data=payload)
    except Exception as e:
        print("Error al enviar mensaje:", e)


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return "No data", 400

    try:
        mensaje = data.get("body", "").strip().lower()
        numero = data.get("from")

        if mensaje.startswith("bateria"):
            partes = mensaje.split(" ")
            if len(partes) == 2:
                placa = partes[1]
                respuesta = obtener_bateria_por_placa(placa)
            else:
                respuesta = "Formato incorrecto. Usa: bateria ABC123"
        else:
            respuesta = "Hola, soy Lía 🤖. Escribe: bateria [placa] para consultar."

        enviar_mensaje(numero, respuesta)
        return "ok", 200

    except Exception as e:
        print("Error en webhook:", e)
        return "Error interno", 500


if __name__ == "__main__":
    app.run(debug=True)



