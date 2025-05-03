from flask import Flask, request, jsonify
import re
import json
import os
import requests
from urllib.parse import urlparse
from linkscanner import scan_links

app = Flask(__name__)

# Emoji-Datenbank laden
with open("emojiDatabase.json", "r", encoding="utf-8") as f:
    emoji_data = json.load(f)

# Funktion zur Emoji-Analyse
def analyze_emojis(text):
    results = []
    for entry in emoji_data:
        if entry["emoji"] in text:
            results.append({
                "warning": f"Emoji-Warnung: {entry['title']} – {entry['text']}",
                "tip": f"ℹ️ Mehr dazu: {entry['link']}",
                "source": "https://www.campact.de/emoji-codes/"
            })
    return results

@app.route("/analyze", methods=["POST"])
def analyze_text():
    data = request.get_json()
    user_text = data.get("text", "")

    feedback = []

    # Fall 1: Kreditkartennummer erkennen
    if re.search(r"\b(?:\d[ -]*?){13,16}\b", user_text):
        feedback.append({
            "warning": "Bitte keine Kreditkartennummern öffentlich teilen.",
            "tip": "Nutze verschlüsselte Kanäle wie Signal oder E-Mail mit PGP.",
            "source": "https://www.bsi.bund.de"
        })

    # Fall 2: Standortangabe
    if re.search(r"\b(im urlaub|bin gerade in|reise nach)\b", user_text.lower()):
        feedback.append({
            "warning": "Standortangaben können deine Abwesenheit verraten.",
            "tip": "Poste Urlaubsinfos erst nach deiner Rückkehr.",
            "source": "https://www.polizei-beratung.de"
        })

    # Fall 3: Klarnamen mit Kritik
    if re.search(r"mein chef|mein arbeitgeber|bei der firma", user_text.lower()) and re.search(r"katastrophe|unfähig|idiot|schrecklich", user_text.lower()):
        feedback.append({
            "warning": "Kritik mit Klarnamen kann rechtliche Folgen haben.",
            "tip": "Formuliere anonymisiert und sachlich.",
            "source": "https://www.datenschutz.org/arbeitnehmerdatenschutz/"
        })

    # Fall 4: Gesundheitsdaten und Screenshots
    if re.search(r"(attest|diagnose|krankmeldung|arzt|krankenhaus)", user_text.lower()):
        feedback.append({
            "warning": "Gesundheitsdaten sind besonders sensibel.",
            "tip": "Teile keine medizinischen Dokumente öffentlich.",
            "source": "https://www.bfdi.bund.de/"
        })
    if "(screenshot" in user_text.lower():
        feedback.append({
            "warning": "Screenshots enthalten oft persönliche Daten.",
            "tip": "Unkenntlich machen oder vermeiden.",
            "source": "https://www.datenschutzkonferenz-online.de/"
        })

    # Fall 5: Linkanalyse
    link_warnings = scan_links(user_text)
    for result in link_warnings:
        feedback.append({
            "warning": result["result"],
            "tip": "Klicke nur auf vertrauenswürdige Quellen.",
            "source": "https://transparencyreport.google.com/safe-browsing"
        })

    # Fall 6: Emoji-Warnungen
    emoji_results = analyze_emojis(user_text)
    feedback.extend(emoji_results)

    # Fallback
    if not feedback:
        return jsonify({
            "warning": "✅ Dein Text enthält keine offensichtlichen Risiken.",
            "tip": "Achte trotzdem auf sensible Daten wie Ort, Namen oder Dokumente.",
            "source": ""
        })

    # Gib den ersten passenden Warnhinweis zurück
    return jsonify(feedback[0])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host="0.0.0.0", port=port)
