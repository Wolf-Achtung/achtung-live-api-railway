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
        return f"API-Key fehlt"

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
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        result = response.json()
        return "unsicher" if result.get("matches") else "sicher"
    except Exception as e:
        return f"Fehler bei der URL-Prüfung: {str(e)}"

def check_all_urls(text):
    urls = re.findall(r'https?://[^\s]+', text)
    if not urls:
        return ""
    results = []
    for url in urls:
        status = check_url_safety(url)
        if status == "unsicher":
            results.append(f"⚠️ Der Link {url} gilt als *unsicher*.")
        elif status == "sicher":
            results.append(f"✅ Link geprüft: {url} scheint unbedenklich.")
        else:
            results.append(f"❗ Konnte {url} nicht prüfen ({status})")
    return "\n".join(results)

def analyze(text):
    iban_pattern = r'\b[A-Z]{2}\d{2}[ ]?\d{4}[ ]?\d{4}[ ]?\d{4}[ ]?\d{4}(?:[ ]?\d{2})?\b'
    simple_iban_pattern = r'\b\d{10,20}\b'

    result_list = []

    if re.search(iban_pattern, text) or re.search(simple_iban_pattern, text):
        result_list.append("Achtung: Teile sensible Bankdaten wie IBANs niemals öffentlich.")
    if "passwort" in text.lower():
        result_list.append("Achtung: Dein Passwort solltest du niemals teilen – ändere es regelmäßig.")
    if "krankheit" in text.lower() or "depression" in text.lower():
        result_list.append("Denke daran: Gesundheitsthemen sind sehr privat. Achte auf deine digitale Privatsphäre.")

    url_feedback = check_all_urls(text)
    if url_feedback:
        result_list.append(url_feedback)

    if not result_list:
        return "Alles gut: Dein Text enthält keine offensichtlichen sensiblen Daten."
    return "\n\n".join(result_list)

if __name__ == '__main__':
    app.run(debug=True)
