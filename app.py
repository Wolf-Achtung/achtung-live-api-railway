from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import os

app = Flask(__name__)
CORS(app)

# Dummy-Sicherheitsbewertung
def simple_score(text):
    text_lower = text.lower()
    if any(word in text_lower for word in ["iban", "kreditkarte", "telefonnummer", "handynummer"]):
        return 85, "🔴 Hohes Risiko erkannt (85 %)"
    elif "foto" in text_lower or "peinlich" in text_lower:
        return 40, "🟡 Mittleres Risiko erkannt (40 %)"
    return 5, "🟢 Kein Risiko erkennbar (5 %)"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"score": 0, "message": "⚠️ Kein gültiger Text erkannt."}), 400
    score, message = simple_score(text)
    return jsonify({"score": score, "message": message})

@app.route("/debug-gpt", methods=["POST"])
def debug_gpt():
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"gpt_raw": "Bitte gib einen Text ein, den ich analysieren kann."})

    # GPT-Antwort Dummy-Version
    text_lower = text.lower()
    if "iban" in text_lower:
        gpt_text = "Das sieht aus wie eine Bankverbindung. Du solltest lieber schreiben: [Bankdaten] oder es weglassen."
    elif "foto" in text_lower and "besoffen" in text_lower:
        gpt_text = "Dieser Text könnte peinlich wirken. Du könntest stattdessen schreiben: 'Hier das lustige Bild von der Feier'."
    elif "telefonnummer" in text_lower or re.search(r"\b01\d{7,}\b", text_lower):
        gpt_text = "Persönliche Telefonnummern gehören nicht ins Netz. Ersetze sie besser mit: [Handynummer]."
    else:
        gpt_text = "Keine sensiblen Inhalte erkannt."

    return jsonify({"gpt_raw": gpt_text})

@app.route("/", methods=["GET"])
def index():
    return "✅ achtung.live API ist aktiv."