from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import json
from linkscanner import scan_links

app = Flask(__name__)
CORS(app)  # 🔓 CORS aktivieren – wichtig für fetch() von extern

# Textmuster
text_patterns = [
    {"pattern": r"\b(kreditkartennummer|iban|kontonummer|zahlung)\b", "feedback": "Bitte keine Zahlungsdaten öffentlich teilen."},
    {"pattern": r"\b(attest|krankenkasse|arzt|diagnose|gesundheit)\b", "feedback": "Vermeide es, Gesundheitsdaten öffentlich zu machen."},
    {"pattern": r"\b(chef|vorgesetzter|firma|arbeitsplatz|arbeitgeber|müller \+ partner)\b", "feedback": "Kritik mit Klarnamen kann rechtliche Folgen haben."},
    {"pattern": r"\b(urlaub|reise|ausland|fliegen|am strand)\b", "feedback": "Reiseinfos können Einbrecher aufmerksam machen – lieber diskret teilen."},
    {"pattern": r"screenshot|whatsapp|chat|messenger", "feedback": "Screenshots können sensible Daten enthalten – Vorsicht bei Weitergabe."}
]

# Emoji-Datenbank laden
try:
    with open("emojiDatabase.json", encoding="utf-8") as f:
        emoji_data = json.load(f)
except:
    emoji_data = {}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "API online", "usage": "POST text to /analyze"})

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    text = data.get("text", "")
    feedback = []

    # Musterprüfung
    for rule in text_patterns:
        if re.search(rule["pattern"], text, re.IGNORECASE):
            feedback.append(rule["feedback"])

    # Emoji-Prüfung
    for emoji, hinweis in emoji_data.items():
        if emoji in text:
            feedback.append(f"Emoji-Warnung: {hinweis}")

    # Linkanalyse
    link_feedback = scan_links(text)
    if link_feedback:
        feedback.extend(link_feedback)

    if not feedback:
        feedback.append("⚠️ Hinweis: Dein Text enthält keine offensichtlichen Risiken – überprüfe dennoch sensible Infos wie Ort, Namen oder Screenshots.")

    return jsonify({"feedback": feedback})
