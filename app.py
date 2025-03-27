from flask import Flask, request
import requests

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "No data", 400

    try:
        message = data.get("data", [])[0]
        message_text = message.get("body", "").lower()
        sender = message.get("from")

        if not sender or not message_text:
            return "Invalid message", 400

        # Procesar palabra clave
        if "bateria" in message_text:
            placa = message_text.replace("bateria", "").strip().upper()
            try:
                response = requests.get("https://redgps-proxy.onrender.com/activos")
                if response.status_code != 200:
                    raise Exception("Error en proxy RedGPS")

                unidades = response.json()
                unidad = next((u for u in unidades if u.get("UnitPlate") == placa), None)

                if unidad:
                    bateria = unidad.get("BateriaGps", "N/A")
                    fecha = unidad.get("ReportDate", "N/A")
                    mensaje = f"🔋 Batería de {placa}: {bateria}%\nÚltimo reporte: {fecha}"
                else:
                    mensaje = f"No encontré información para la placa {placa}."

            except Exception as e:
                mensaje = f"Error al consultar datos de RedGPS. Intenta nuevamente."
        else:
            mensaje = "Hola, soy Lía 🤖. Para consultar la batería de una unidad, escribe: *bateria [placa]*."

        # Enviar respuesta al mismo número
        requests.post("https://api.ultramsg.com/instance111839/messages/chat", data={
            "token": "r4wm8253iqivpbku",
            "to": sender,
            "body": mensaje
        })

        return "OK", 200

    except Exception as e:
        return f"Error interno: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

