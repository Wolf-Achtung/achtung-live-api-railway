from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import json
from linkscanner import scan_links

app = Flask(__name__)
CORS(app)

# 🔁 Lade Emoji-Datenbank
with open("emojiDatabase.json", "r", encoding="utf-8") as f:
    emoji_data = json.load(f)

# 🧠 Kritische Begriffe und Hinweise mit Tipps
sensitive_keywords = {
    "kreditkarte": {
        "warnung": "Bitte keine Zahlungsdaten öffentlich teilen.",
        "tipp": "Sende Zahlungsinformationen nur über sichere Kanäle wie verschlüsselte Messenger oder E-Mail mit PGP."
    },
    "iban": {
        "warnung": "IBAN-Nummern können für Phishing oder Zahlungsbetrug missbraucht werden.",
        "tipp": "Gib deine IBAN nur über geprüfte, verschlüsselte Wege weiter."
    },
    "krankenkasse": {
        "warnung": "Gesundheitsdaten sind besonders sensibel.",
        "tipp": "Vermeide das Teilen medizinischer Dokumente – nutze sichere Übertragungswege wie verschlüsselte E-Mail."
    },
    "attest": {
        "warnung": "Medizinische Informationen sollten niemals öffentlich geteilt werden.",
        "tipp": "Nutze geschützte Plattformen oder Cloud-Dienste mit Zugriffskontrolle."
    },
    "urlaub": {
        "warnung": "Standortangaben oder Urlaubspläne können ein Einbruchsrisiko darstellen.",
        "tipp": "Teile Urlaubsbilder oder Reiseinfos erst nach deiner Rückkehr."
    },
    "chef": {
        "warnung": "Kritik mit Klarnamen kann rechtliche Folgen haben.",
        "tipp": "Formuliere sachlich und vermeide die Nennung von Personen oder Firmen."
    },
    "firma": {
        "warnung": "Öffentliche Aussagen über Arbeitgeber können zu Abmahnungen führen.",
        "tipp": "Beschreibe die Situation neutral, ohne Namensnennung."
    },
    "screenshot": {
        "warnung": "Screenshots enthalten oft persönliche Daten oder Klarnamen.",
        "tipp": "Verwende anonymisierte Screenshots oder unkenntlich gemachte Inhalte."
    }
}

def detect_sensitive_keywords(text):
    findings = []
    text_lower = text.lower()
    for keyword, info in sensitive_keywords.items():
        if keyword in text_lower:
            findings.append({
                "risiko": keyword,
                "warnung": info["warnung"],
                "tipp": info["tipp"]
            })
    return findings

def detect_emojis(text):
    found = []
    for emoji, entry in emoji_data.items():
        if emoji in text:
            found.append({
                "emoji": emoji,
                "title": entry.get("title", ""),
                "text": entry.get("text", ""),
                "group": entry.get("group", ""),
                "link": entry.get("link", "")
            })
    return found

@app.route("/")
def home():
    return "achtung.live API läuft."

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    text = data.get("text", "")
    
    if not text:
        return jsonify({"error": "Kein Text übergeben."}), 400

    feedback = []
    keywords = detect_sensitive_keywords(text)
    if keywords:
        for match in keywords:
            feedback.append(f"⚠️ Hinweis: {match['warnung']}\n💡 Tipp: {match['tipp']}")
    
    emojis = detect_emojis(text)
    for match in emojis:
        info = f"⚠️ Hinweis: Emoji-Warnung: {match['title']} – {match['text']}"
        if match["link"]:
            info += f"\nℹ️ Mehr dazu: {match['link']}"
        feedback.append(info)

    links = re.findall(r'https?://\S+', text)
    if links:
        link_feedback = scan_links(links)
        for entry in link_feedback:
            status = "🚨 Verdächtiger Link erkannt" if entry["risk"] else "✅ Link geprüft"
            info = entry.get("reason", "")
            feedback.append(f"⚠️ Hinweis: {status}: {entry['url']} {info}")

    if not feedback:
        feedback.append("⚠️ Hinweis: Dein Text enthält keine offensichtlichen Risiken – überprüfe dennoch sensible Infos wie Ort, Namen oder Screenshots.")

    return jsonify({"feedback": feedback})

if __name__ == "__main__":
    app.run(debug=True)
