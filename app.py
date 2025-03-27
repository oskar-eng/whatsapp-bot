from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Configuraciones
ULTRAMSG_TOKEN = "r4wm825i3lqivpku"
ULTRAMSG_INSTANCE = "instance111839"
REDGPS_PROXY_URL = "https://redgps-proxy.onrender.com/activos"

# Ruta para el webhook de UltraMsg
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if not data:
        return "No JSON", 400

    try:
        mensaje = data['body'].strip().lower()
        telefono = data['from']

        if mensaje.startswith("bateria"):
            partes = mensaje.split()
            if len(partes) >= 2:
                placa = partes[1].upper()
                return consultar_y_responder_bateria(telefono, placa)

        enviar_respuesta(telefono, "😊 Hola, soy Lía. Puedes escribirme `bateria [placa]` para consultar el nivel de batería.")

    except Exception as e:
        print("Error en webhook:", e)
    
    return "OK", 200


def consultar_y_responder_bateria(telefono, placa):
    try:
        respuesta = requests.get(f"{REDGPS_PROXY_URL}?placa={placa}")
        if respuesta.status_code == 200:
            datos = respuesta.json()
            bateria = datos.get("bateria", "desconocida")
            ultima = datos.get("ultimoReporte", "-")
            mensaje = f"⚡ Batería de {placa}: {bateria}%\n⏰ Último reporte: {ultima}"
        else:
            mensaje = f"No encontré datos para la placa {placa}."
    except Exception as e:
        print("Error al consultar RedGPS Proxy:", e)
        mensaje = "Lo siento, hubo un error al consultar la batería."

    enviar_respuesta(telefono, mensaje)
    return "OK", 200


def enviar_respuesta(telefono, mensaje):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE}/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": telefono,
        "body": mensaje
    }
    try:
        r = requests.post(url, data=payload)
        print("Respuesta enviada:", r.status_code)
    except Exception as e:
        print("Error al enviar respuesta:", e)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)


