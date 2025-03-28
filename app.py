from flask import Flask, request
import os
import csv

app = Flask(__name__)

# Ruta al archivo CSV local con los datos
CSV_LOCAL_FILE = "datos.csv"

def obtener_datos_placa(placa):
    try:
        with open(CSV_LOCAL_FILE, newline='', encoding='utf-8') as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                if fila['placa'].strip().upper() == placa.upper():
                    return {
                        'placa': fila['placa'],
                        'imei': fila['imei'],
                        'bateria': fila['bateria'],
                        'fecha': fila['fecha'],
                    }
        return None
    except Exception as e:
        print("Error al leer el archivo CSV:", e)
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
                texto = f"🔋 Batería del GPS de {resultado['placa']}: {resultado['bateria']}%\n📅 Último reporte: {resultado['fecha']}"
            else:
                texto = f"🚫 No encontré información para la placa '{placa.upper()}'"
        else:
            texto = "Por favor indica la placa: Ejemplo 'bateria CE-049040'"
    else:
        texto = "Hola, soy Lía 🤖. Puedes consultarme escribiendo: bateria [placa]"

    # Responder usando UltraMsg
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

