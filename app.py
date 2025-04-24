from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import re

app = Flask(__name__)
CORS(app)

openai.api_key = "DEIN_OPENAI_API_KEY"  # 🔁 als Umgebungsvariable setzen im Live-Betrieb

# Sensible Begriffe, die Risiko markieren
HIGH_RISK = [
    "kreditkarte", "kreditkartennummer", "kartennummer", "iban", "kontonummer",
    "passwort", "diagnose", "depression", "trauma", "suizid", "medikament",
    "kind", "adresse", "chef", "krankheit", "login", "token", "gesundheit"
]

TIPP_MAPPING = {
    "kreditkarte": "Verwende Einwegkarten oder sichere Dienste wie Klarna oder Apple Pay.",
    "kreditkartennummer": "Veröffentliche deine Kartennummer niemals öffentlich – sie kann sofort missbraucht werden.",
    "iban": "Gib deine IBAN nur verschlüsselt weiter – nicht im Klartext.",
    "passwort": "Teile niemals Passwörter – nicht einmal Auszüge.",
    "depression": "Psychische Themen verdienen Schutz. Sprich vertraulich – nicht öffentlich.",
    "suizid": "Du bist nicht allein. Hilfe: 0800 111 0 111 oder telefonseelsorge.de",
    "chef": "Berufliche Konflikte lieber nicht öffentlich austragen.",
    "kind": "Daten zu Kindern (z. B. Namen, Fotos) nie öffentlich teilen.",
    "medikament": "Gesundheitsdaten gelten als besonders sensibel – teile sie geschützt.",
}

def determine_risk_level(text):
    text_lower = text.lower()
    detected = [word for word in HIGH_RISK if re.search(rf"\b{word}\b", text_lower)]
    
    if detected:
        tip = " ".join([TIPP_MAPPING.get(word, "") for word in detected])
        return (
            "🔴 Kritisch",
            "Diese Info solltest du nur vertraulich teilen.",
            tip if tip else "Bitte über sichere Kanäle wie verschlüsselte E-Mail senden.",
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
            {"role": "system", "content": "Formuliere sensible Texte datenschutzgerecht, empathisch und anonymisiert um."},
            {"role": "user", "content": f"Bitte mach diesen Text datenschutzgerecht: {text}"}
        ]
    )
    return response.choices[0].message.content.strip()

def generate_howto():
    return """\
🔐 So versendest du deine Nachricht sicher:
1. Erstelle ein Konto bei https://proton.me
2. Verfasse deine Nachricht
3. Klicke auf das Schloss-Symbol (🔒), setze ein Passwort
4. Teile das Passwort separat
5. Empfänger kann deine Nachricht entschlüsseln – sicher & privat
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
        "empathy_message": "Das klingt persönlich. Wir helfen dir beim sicheren Umschreiben." if detected else "",
        "empathy_level": "empathy-box" if detected else "",
        "rewrite_offer": "true" if detected else "",
        "howto": "true" if any(w in text.lower() for w in ["iban", "kreditkarte", "kreditkartennummer"]) else ""
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
