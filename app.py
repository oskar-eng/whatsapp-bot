from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Bot WhatsApp Lía está activo 🟢", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON received"}), 400

        message = data.get("body", "").strip().lower()
        sender = data.get("from", "")

        if not message or not sender:
            return jsonify({"error": "Missing 'body' or 'from'"}), 400

        if message.startswith("bateria"):
            partes = message.split(" ")
            if len(partes) == 2:
                placa = partes[1].upper()
                return procesar_bateria(sender, placa)
            else:
                enviar_mensaje(sender, "❌ Usa el formato correcto: bateria [placa]")
        else:
            enviar_mensaje(sender, "👋 Hola, soy Lía. Escribe *bateria [placa]* para consultar la batería GPS.")
        
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

def procesar_bateria(numero, placa):
    try:
        # Aquí llamamos al API del proxy RedGPS
        url = "https://redgps-proxy.onrender.com/activos"
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers)
        data = response.json()

        for unidad in data.get("data", []):
            if unidad.get("UnitPlate", "").upper() == placa:
                mensaje = f"📍 *{unidad.get('UnitId')}*\n🔋 Batería: {unidad.get('BateriaGps')}\n🕒 Último reporte: {unidad.get('ReportDate')}"
                enviar_mensaje(numero, mensaje)
                return jsonify({"status": "enviado"}), 200

        enviar_mensaje(numero, f"🚫 No se encontró la placa {placa}.")
        return jsonify({"status": "placa no encontrada"}), 200

    except Exception as e:
        print("Error al consultar RedGPS:", e)
        enviar_mensaje(numero, "❌ Error al consultar la batería.")
        return jsonify({"error": str(e)}), 500

def enviar_mensaje(numero, mensaje):
    instancia_id = "111839"
    token = "r4wm825i3lqivpku"
    url = f"https://api.ultramsg.com/instance{instancia_id}/messages/chat"
    payload = {
        "token": token,
        "to": numero,
        "body": mensaje
    }
    requests.post(url, data=payload)

if __name__ == "__main__":
    app.run(debug=True, port=10000, host="0.0.0.0")




