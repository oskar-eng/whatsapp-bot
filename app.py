from flask import Flask, request
import requests
import os
import csv
from io import StringIO

app = Flask(__name__)

SHEET_CSV_URL = os.getenv("https://docs.google.com/spreadsheets/d/e/2PACX-1vSDN1EJPh4tLtxFxMbmK_s5eKZxvA8CcaPKVl5LFPSaaRuizjME_wgCefpn-JgZ0Z7ZDd1sAZ0SO27h/pub?gid=0&single=true&output=csv")  # <-- agrega esto en Render como variable de entorno
ULTRA_INSTANCE = os.getenv("instance111839")
ULTRA_TOKEN = os.getenv("o4ef8592pscczodm")


def buscar_placa(placa_busqueda):
    try:
        response = requests.get(SHEET_CSV_URL)
        content = StringIO(response.text)
        reader = csv.DictReader(content)

        for row in reader:
            if row["placa"].strip().upper() == placa_busqueda.upper():
                return row
        return None
    except Exception as e:
        print("Error al consultar Google Sheets:", e)
        return None


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data or "message" not in data:
        return "OK"

    mensaje = data["message"]["body"].strip()
    numero = data["message"]["from"]

    if mensaje.lower().startswith("bateria"):
        partes = mensaje.split()
        if len(partes) >= 2:
            placa = " ".join(partes[1:])
            resultado = buscar_placa(placa)

            if resultado:
                texto = f"🔋 Batería del GPS de {resultado['placa']}: {resultado['bateria']}%\n📅 Último reporte: {resultado['fecha']}"
            else:
                texto = f"🚫 No encontré información para la placa '{placa.upper()}'. Verifica si está bien escrita."
        else:
            texto = "⚠️ Usa el formato: bateria [placa]. Ejemplo: bateria ABC-123"
    else:
        texto = "👋 Hola, soy Lía. Para consultar la batería de una unidad, escribe:\n👉 *bateria [placa]*\nEjemplo: bateria ABC-123"

    payload = {
        "token": ULTRA_TOKEN,
        "to": numero,
        "body": texto
    }
    requests.post(f"https://api.ultramsg.com/{ULTRA_INSTANCE}/messages/chat", data=payload)
    return "OK"


if __name__ == "__main__":
    app.run(debug=True, port=10000)

