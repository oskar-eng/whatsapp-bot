@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # ✅ Detecta si viene como JSON o Form
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        print("Datos recibidos:", data)  # Debug

        message = data.get("body", "").strip().lower()
        sender = data.get("from", "")

        if not message or not sender:
            return jsonify({"error": "Faltan campos 'body' o 'from'"}), 400

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
        print("❌ Error en webhook:", e)
        return jsonify({"error": str(e)}), 500




