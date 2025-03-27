from flask import Flask, request
import requests
import os

app = Flask(__name__)

# URL de Google Sheets (formato CSV)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSF2EssaBoWeEnfowYUJcBv3GXKIWWjOHbwQT7NhehHg2lF0IEgFXrFNbrgwFVr4C5NunL85Vfe9AOs/pub?gid=0&single=true&output=csv"

def obtener_datos_placa(placa):
    try:
        respuesta = requests.get(SHEET_CSV_URL)
        filas = respuesta.text.splitlines()
        for fila in filas[1:]:
            datos = fila.split(',')
            if datos[0].strip().upper() == placa.upper():
                return {
                    'placa': datos[0],
                    'imei': datos[1],
                    'bateria': datos[2],
                    'fecha': datos[3]
                }
        return None
    except Exception as e:
        print("Error leyendo hoja:", e)
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
            resultado = obtener_datos_placa(placa)
            if resultado:
                texto = f"🔋 Batería GPS de {resultado['placa']}: {resultado['bateria']}%\n📅 Último reporte: {resultado['fecha']}"
            else:
                texto = f"❌ No encontré datos para la placa '{placa.upper()}'."
        else:
            texto = "🔍 Por favor escribe la placa. Ejemplo: `bateria ADH-871`"
    else:
        texto = "👋 Hola, soy Lía. Puedes escribirme: `bateria [placa]` para saber el nivel de batería GPS."

    # Enviar respuesta vía UltraMsg
    payload = {
        "token": os.getenv("ULTRA_TOKEN"),
        "to": numero,
        "body": texto
    }
    instancia = os.getenv("ULTRA_INSTANCE")
    requests.post(f"https://api.ultramsg.com/{instancia}/messages/chat", data=payload)

    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # <-- Asegura que escuche el puerto que Render asigna
    app.run(host="0.0.0.0", port=port)

