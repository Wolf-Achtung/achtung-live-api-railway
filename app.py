from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def index():
    return "✅ achtung.live API ist aktiv."

@app.route("/debug-gpt", methods=["POST"])
def debug_gpt():
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text or len(text) < 5:
        return jsonify({"gpt_raw": "Bitte gib einen vollständigen Text ein, den ich bewerten kann."})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Du bist ein Datenschutz- und Kommunikationsberater."},
                {"role": "user", "content": f"""
Analysiere folgenden Text auf Datenschutz- oder Kommunikationsrisiken:

"{text}"

Gib eine klare, freundliche Empfehlung in 1–2 Sätzen, wie der Text sicherer formuliert werden kann.
Keine JSON-Ausgabe. Keine Zusammenfassung. Nur die Empfehlung selbst.
"""}
            ],
            temperature=0.7,
            max_tokens=150
        )

        gpt_tip = response.choices[0].message.content.strip()
        return jsonify({"gpt_raw": gpt_tip})

    except Exception as e:
        return jsonify({"gpt_raw": f"⚠️ GPT-Fehler: {str(e)}"})