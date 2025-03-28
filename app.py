from flask import Flask, request
import requests
import os

app = Flask(__name__)

# URL de la hoja de cálculo publicada como CSV
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSF2EssaBoWeEnfowYUJcBv3GXKIWWjOHbwQT7NhehHg2lF0IEgFXrFNbrgwFVr4C5NunL85Vfe9AOs/pub?gid=0&single=true&output=csv"


def obtener_datos_placa(placa):
    try:
        respuesta = requests.get(SHEET_CSV_URL)
        filas = respuesta.text.splitlines()
        encabezados = filas[0].split(',')

        for fila in filas[1:]:
            datos = fila.split(',')
            if datos[0].strip().upper() == placa.upper():
                return {
                    'placa': datos[0],
                    'imei': datos[1],
                    'bateria': datos[2],
                    'fecha': datos[3],
                }
        return None
    except Exception as e:
        print("Error al leer la hoja:", e)
        return None


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data or "message" not in data:
        return "OK"

    mensaje = data["message"]["body"].strip().lower()
    numero = data["message"]["from"]

    if mensaje.startswith("bateria"):
        partes = mensaje.split()
        if len(partes) >= 2:
            placa = " ".join(partes[1:]).strip()
            resultado = obtener_datos_placa(placa)

            if resultado:
                texto = f"🔋 Batería del GPS de {resultado['placa']}: {resultado['bateria']}%\n📅 Último reporte: {resultado['fecha']}"
            else:
                texto = f"🚫 No encontré información para la placa '{placa.upper()}'"
        else:
            texto = "❗ Por favor indica la placa. Ejemplo: bateria CE-049040"
    else:
        texto = "Hola, soy Lía 🤖. Puedes escribirme: bateria [placa] para consultar el estado del GPS."

    # Enviar respuesta usando UltraMsg
    instancia_id = os.getenv("ULTRA_INSTANCE", "instance111839")
    token = os.getenv("ULTRA_TOKEN", "r4wm825i3lqivpku")

    payload = {
        "token": token,
        "to": numero,
        "body": texto
    }

    requests.post(f"https://api.ultramsg.com/{instancia_id}/messages/chat", data=payload)

    return "OK"


if __name__ == '__main__':
    app.run(debug=True, port=10000)


