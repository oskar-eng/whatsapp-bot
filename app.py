from flask import Flask, request
import requests
import os

app = Flask(__name__)

ULTRAMSG_INSTANCE_ID = "instance111839"
ULTRAMSG_TOKEN = "r4wm825i3lqivpku"
RECEIVER_PHONE = ""  # Esto lo asignaremos desde los mensajes entrantes

REDGPS_API_URL = "https://api.service24gps.com/api/v1/getdata"
REDGPS_APIKEY = "255dsd2342340893dsdsdS7c0118e72"
REDGPS_TOKEN = "8JKsNtW/HT87wxaSZLIsfyEFURGYUg4BOoo6swqPm9XHCY7nKtP+34bzOO8pvK7Q"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    try:
        message = data['body'].get('text', '').strip()
        sender = data['from']

        if message.lower().startswith("bateria"):
            partes = message.split()
            if len(partes) == 2:
                placa = partes[1]
                bateria = obtener_bateria_por_placa(placa)
                respuesta = f"La batería de la unidad {placa} es {bateria}%"
            else:
                respuesta = "Formato incorrecto. Usa: bateria [placa]"
        else:
            respuesta = "Hola, soy Lía 🧠. Puedes consultarme con: bateria [placa]"

        enviar_mensaje(sender, respuesta)
        return "ok", 200
    except Exception as e:
        print("Error:", e)
        return "error", 500

def obtener_bateria_por_placa(placa):
    payload = {
        "apikey": REDGPS_APIKEY,
        "token": REDGPS_TOKEN,
        "UseUTCDate": "0",
        "sensores": "1"
    }
    try:
        response = requests.post(REDGPS_API_URL, data=payload)
        data = response.json()
        for unidad in data["data"]:
            if unidad.get("UnitId", "").lower() == placa.lower():
                return unidad.get("BatteryGps", "Desconocido")
        return "No encontrada"
    except Exception as e:
        print("Error en API RedGPS:", e)
        return "Error"

def enviar_mensaje(to, mensaje):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    data = {
        "token": ULTRAMSG_TOKEN,
        "to": to,
        "body": mensaje
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Error al enviar mensaje:", e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)


