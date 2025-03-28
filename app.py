from flask import Flask, request
import requests
import os
import csv
from io import StringIO

app = Flask(__name__)

# URL del CSV publicado desde Google Sheets (reemplázalo por el tuyo)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQCIQ0FHfnImrxWmheLX9BEZ8Bm6GaK50DRSrhsTbH3BA9z0ggnnMfOOoTytO_fQTg5j2z7qyo3rds9/pub?gid=560326357&single=true&output=csv"

def obtener_datos_placa(placa):
    try:
        response = requests.get(SHEET_CSV_URL)
        response.encoding = 'utf-8'
        data = csv.DictReader(StringIO(response.text))

        for fila in data:
            if fila['placa'].strip().upper() == placa.upper():
                return fila
        return None
    except Exception as e:
        print(f"Error leyendo CSV: {e}")
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
            placa = " ".join(partes[1:])
            datos = obtener_datos_placa(placa)
            if datos:
                texto = f"🔋 Batería del GPS de {datos['placa']}: {datos['bateria']}%\n📅 Último reporte: {datos['fecha']}"
            else:
                texto = f"🚫 No encontré información para la placa '{placa.upper()}'"
        else:
            texto = "❗Formato incorrecto. Escribe: bateria [placa]\nEjemplo: bateria CE-049040"
    else:
        texto = "🤖 Comando no reconocido. Escribe: bateria [placa]"

    # Enviar respuesta usando UltraMsg
    instancia_id = os.getenv("instance111839")
    token = os.getenv("o4ef8592pscczodm")

    payload = {
        "token": token,
        "to": numero,
        "body": texto
    }
    requests.post(f"https://api.ultramsg.com/{instancia_id}/messages/chat", data=payload)

    return "OK"

if __name__ == '__main__':
    app.run(debug=True, port=10000)

