from flask import Flask, request, jsonify
import re
import os
import requests

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze_text():
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "Kein Text übermittelt."}), 400

    text = data['text']
    result = analyze(text)

    return jsonify({"analysis": result})

def check_url_safety(url):
    api_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
    if not api_key:
        return "Fehlender API-Key"
    
    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
    payload = {
        "client": {
            "clientId": "achtung.live",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(endpoint, json=payload, headers=headers)
    
    result = response.json()
    return "unsicher" if result.get("matches") else "sicher"

def analyze(text):
    # Beispiel: Suche nach IBAN (vereinfachtes Muster)
    iban_pattern = r'\b[A-Z]{2}\d{2}[ ]?\d{4}[ ]?\d{4}[ ]?\d{4}[ ]?\d{4}(?:[ ]?\d{2})?\b'
    simple_iban_pattern = r'\b\d{10,20}\b'

    if re.search(iban_pattern, text) or re.search(simple_iban_pattern, text):
        return "Achtung: Teile sensible Bankdaten wie IBANs niemals öffentlich."
    elif "passwort" in text.lower():
        return "Achtung: Dein Passwort solltest du niemals teilen – ändere es regelmäßig."
    elif "krankheit" in text.lower() or "depression" in text.lower():
        return "Denke daran: Gesundheitsthemen sind sehr privat. Achte auf deine digitale Privatsphäre."
    else:
        return "Alles gut: Dein Text enthält keine offensichtlichen sensiblen Daten."

if __name__ == '__main__':
    app.run(debug=True)
