from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import re

app = Flask(__name__)
CORS(app)

openai.api_key = "DEIN_OPENAI_API_KEY"  # 🔐 Im Produktivbetrieb als Umgebungsvariable setzen

# Erweiterte Liste sensibler Begriffe
HIGH_RISK = [
    "kreditkarte", "kreditkartennummer", "kreditkarten-nummer", "kartennummer",
    "iban", "kontonummer", "bankverbindung",
    "passwort", "login", "token",
    "diagnose", "krankheit", "medikament", "gesundheit", "depression", "trauma", "suizid",
    "chef", "adresse", "kind", "schule"
]

TIPP_MAPPING = {
    "kreditkarte": "Nutze Einwegkarten oder sichere Dienste wie Klarna oder Apple Pay.",
    "kreditkartennummer": "Kreditkarten-Infos dürfen niemals öffentlich geteilt werden.",
    "kreditkarten-nummer": "Teile deine Kreditkartennummer nie im Klartext.",
    "iban": "IBAN nur verschlüsselt weitergeben – z. B. per passwortgeschützter Datei.",
    "passwort": "Passwörter niemals weitergeben – auch nicht auszugsweise.",
    "depression": "Psychische Themen gehören in einen geschützten Rahmen.",
    "suizid": "Hilfe findest du anonym bei 0800 111 0 111 oder telefonseelsorge.de",
    "kind": "Bitte keine Namen, Fotos oder Daten von Kindern öffentlich machen.",
    "medikament": "Gesundheitsdaten gelten als besonders sensibel – teile sie geschützt.",
}

def keyword_match(word, text):
    return word in text or re.search(rf"\b{re.escape(word)}\b", text)

def determine_risk_level(text):
    text_lower = text.lower()
    detected = [w for w in HIGH_RISK if keyword_match(w, text_lower)]

    if detected:
        tips = [TIPP_MAPPING.get(w, "") for w in detected]
        tip_combined = " ".join([t for t in tips if t])
        return (
            "🔴 Kritisch",
            "Diese Info solltest du nur vertraulich teilen.",
            tip_combined if tip_combined else "Verwende sichere Übertragungswege wie verschlüsselte E-Mails.",
            detected
        )
    return (
        "🟢 Kein Risiko",
        "Keine sensiblen Inhalte erkannt.",
        "Keine Maßnahmen erforderlich.",
        []
    )

def rewrite_text(text):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Formuliere sensible Texte datenschutzgerecht und empathisch um."},
            {"role": "user", "content": f"Bitte mach diesen Text datenschutzgerecht und weniger riskant: {text}"}
        ]
    )
    return response.choices[0].message.content.strip()

def generate_howto():
    return """\
🔐 Anleitung für sichere Kommunikation:
1. Nutze verschlüsselte E-Mail-Dienste wie https://proton.me
2. Verfasse deine Nachricht wie gewohnt
3. Aktiviere Verschlüsselung (Schloss-Symbol), lege Passwort fest
4. Teile Passwort separat
5. Empfänger kann Nachricht entschlüsseln – sicher & DSGVO-konform
"""

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text", "")

    risk_level, explanation, tip, detected = determine_risk_level(text)

    response = {
        "detected_data": ", ".join([f"** {w.title()}" for w in detected]) if detected else "Keine",
        "risk_level": risk_level,
        "explanation": explanation,
        "tip": tip,
        "source": "",
        "empathy_message": "Das klingt sehr persönlich. Wir helfen dir, deinen Text zu schützen." if detected else "",
        "empathy_level": "empathy-box" if detected else "",
        "rewrite_offer": "true" if detected else "",
        "howto": "true" if any(k in text.lower() for k in ["iban", "kreditkarte", "kreditkartennummer", "kreditkarten-nummer"]) else ""
    }

    return jsonify(response)

@app.route("/rewrite", methods=["POST"])
def rewrite():
    text = request.json.get("text", "")
    return jsonify({"rewritten": rewrite_text(text)})

@app.route("/howto", methods=["GET"])
def howto():
    return jsonify({"howto": generate_howto()})

if __name__ == "__main__":
    app.run(debug=True)
