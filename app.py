from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import re

app = Flask(__name__)
CORS(app)

openai.api_key = "DEIN_OPENAI_API_KEY"

HIGH_RISK = [
    "kreditkarte", "kreditkartennummer", "kreditkarten-nummer", "kartennummer",
    "iban", "kontonummer", "bankverbindung",
    "passwort", "login", "token",
    "diagnose", "krankheit", "medikament", "gesundheit", "depression", "trauma", "suizid",
    "chef", "adresse", "kind", "schule", "whatsapp", "screenshot", "urlaub", "standort"
]

TIPP_MAPPING = {
    "kreditkarte": "💳 Nutze <a href='https://privacy.com' target='_blank'>Privacy.com</a> oder <a href='https://www.apple.com/apple-pay/' target='_blank'>Apple Pay</a>. <a href='/hilfe-kreditkarte.html'>Mehr erfahren</a>",
    "iban": "🏦 Übermittle deine IBAN nur verschlüsselt. <a href='/hilfe-iban.html'>Mehr erfahren</a>",
    "passwort": "🔐 Niemals öffentlich teilen. <a href='/hilfe-passwort.html'>So schützt du deine Logins</a>",
    "depression": "🧠 Psychische Gesundheit braucht Schutz. <a href='/hilfe-depression.html'>Hilfreiche Tipps</a>",
    "suizid": "📞 Hilfe findest du anonym bei <a href='https://www.telefonseelsorge.de'>telefonseelsorge.de</a>",
    "kind": "👶 Persönliche Daten von Kindern nie veröffentlichen. <a href='/hilfe-kinder.html'>Warum?</a>",
    "medikament": "💊 Gesundheitsangaben vertraulich teilen. <a href='/hilfe-medikament.html'>Mehr erfahren</a>",
    "whatsapp": "📱 Datenschutzeinstellungen aktivieren! <a href='/hilfe-whatsapp.html'>So geht's</a>",
    "screenshot": "🖼️ Metadaten entfernen vor dem Teilen. <a href='/hilfe-screenshot.html'>Anleitung</a>",
    "urlaub": "🏖️ Urlaub posten? Nur sicher. <a href='/hilfe-urlaub.html'>Risiken & Tipps</a>",
    "chef": "💼 Kritik nur privat äußern. <a href='/hilfe-chef.html'>Warum das wichtig ist</a>",
    "standort": "📍 Teile deinen Standort nicht öffentlich. <a href='/hilfe-standort.html'>Mehr dazu</a>",
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
            tip_combined if tip_combined else "Verwende sichere Übertragungswege.",
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
            {
                "role": "system",
                "content": (
                    "Du hilfst Nutzer:innen, sensible oder riskante Aussagen so umzuformulieren, "
                    "dass sie sicher, respektvoll und datenschutzkonform klingen. "
                    "Statt Zensur schlägst du konkrete Formulierungen vor, "
                    "die dieselbe Botschaft sicherer vermitteln oder alternative, souveräne Wege aufzeigen. "
                    "Wenn angebracht, bietest du Rückfragen oder Empfehlungen an. "
                    "Vermeide KI-Floskeln. Schreibe menschlich, empathisch, klar."
                )
            },
            {
                "role": "user",
                "content": f"Bitte formuliere diesen Text datenschutzgerecht und hilfreich um: {text}"
            }
        ]
    )
    return response.choices[0].message.content.strip()

def generate_howto():
    return """\
🔐 Anleitung für sicheren Versand:
1. Erstelle ein Konto bei <a href='https://proton.me' target='_blank'>ProtonMail</a>
2. Verfasse deine Nachricht
3. Klicke auf 🔒 und setze ein Passwort
4. Teile das Passwort getrennt (z. B. telefonisch)
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
