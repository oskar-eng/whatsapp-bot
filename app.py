from flask import Flask, request
import requests
import os
import csv
import io

app = Flask(__name__)

# URL del CSV publicado desde Google Sheets
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSF2EssaBoWeEnfowYUJcBv3GXKIWWjOHbwQT7NhehHg2lF0IEgFXrFNbrgwFVr4C5NunL85Vfe9AOs/pub?gid=0&single=true&output=csv"


def obtener_datos_por_placa(placa):
    try:
        response = requests.get(SHEET_CSV_URL)
        response.encoding = 'utf-8'
        contenido = response.text
        archivo = csv.DictReader(io.StringIO(contenido))

        for fila in archivo:
            if fila["placa"].strip().upper() == placa.strip().upper():
                return fila
        return None
    except Exception as e:
        print("Error al leer el CSV:", e)
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
            datos = obtener_datos_por_placa(placa)
            if datos:
                texto = f"🔋 Batería del GPS de {datos['placa']}: {datos['bateria']}%\n📅 Último reporte: {datos['fecha']}"
            else:
                texto = f"🚫 No encontré información para la placa '{placa.upper()}'"
        else:
            texto = "Por favor indica la placa: Ejemplo 'bateria CE-049040'"
    else:
        texto = "Hola, soy Lía 🤖. Puedes consultarme escribiendo: bateria [placa]"

    instancia_id = os.getenv("ULTRA_INSTANCE") or "instance111839"
    token = os.getenv("ULTRA_TOKEN") or "r4wm825i3lqivpku"

    payload = {
        "token": token,
        "to": numero,
        "body": texto
    }
    try:
        requests.post(f"https://api.ultramsg.com/{instancia_id}/messages/chat", data=payload)
    except Exception as e:
        print("Error al enviar mensaje:", e)

    return "OK"


if __name__ == '__main__':
    app.run(debug=True, port=10000)

