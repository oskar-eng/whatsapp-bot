from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configuración UltraMsg
ULTRAMSG_INSTANCE = "111839"
ULTRAMSG_TOKEN = "r4wm825i3qlivpku"

# Configuración RedGPS Proxy (con token rotativo)
REDGPS_PROXY_URL = "https://redgps-proxy.onrender.com/activos"

def enviar_mensaje(numero, mensaje):
    url = f"https://api.ultramsg.com/instance{ULTRAMSG_INSTANCE}/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": numero,
        "body": mensaje
    }
    try:
        response = requests.post(url, data=payload)
        print("✅ Enviado:", response.text)
    except Exception as e:
        print("❌ Error al enviar mensaje:", e)

def obtener_datos_redgps():
    try:
        response = requests.get(REDGPS_PROXY_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("❌ Error al obtener datos de RedGPS:", e)
        return []

def procesar_bateria(numero, placa):
    datos = obtener_datos_redgps()
    if not datos:
        enviar_mensaje(numero, "❌ No se pudieron obtener los datos de RedGPS.")
        return

    for unidad in datos:
        if unidad.get("UnitPlate", "").upper() == placa.upper():
            mensaje = (
                f"🔋 *Batería GPS* de *{placa}*: {unidad.get('BateriaGps')}%\n"
                f"📅 Último reporte: {unidad.get('ReportDate')}"
            )
            enviar_mensaje(numero, mensaje)
            return

    enviar_mensaje(numero, f"❌ No se encontró la placa {placa} en RedGPS.")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        print("📥 Datos recibidos:", data)

        message = data.get("body", "").strip().lower()
        sender = data.get("from", "")

        if not message or not sender:
            return jsonify({"error": "Faltan campos 'body' o 'from'"}), 400

        if message.startswith("bateria"):
            partes = message.split(" ")
            if len(partes) == 2:
                placa = partes[1].upper()
                procesar_bateria(sender, placa)
            else:
                enviar_mensaje(sender, "❌ Usa el formato correcto: bateria [placa]")
        else:
            enviar_mensaje(sender, "👋 Hola, soy Lía. Escribe *bateria [placa]* para consultar la batería del GPS.")

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("❌ Error general:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "👋 Bot de WhatsApp activo."






