from flask import Flask, request, jsonify
from flask_cors import CORS
from linkscanner import analyze_text
import os
import openai

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "✅ achtung.live API ist aktiv."

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    text = data.get("text", "")
    result = analyze_text(text)
    return jsonify(result)

@app.route("/debug-gpt", methods=["POST"])
def debug_gpt():
    data = request.get_json()
    text = data.get("text", "")

    openai.api_key = os.getenv("OPENAI_API_KEY")

    try:
        gpt_prompt = (
            "Bewerte den folgenden Text mit einem JSON-Objekt im Markdown-Format. "
            "Antworte NICHT mit zusätzlichem Text, nur mit:\n"
            "\n```json\n{\n"
            "\"sem_risk_level\": \"hoch|mittel|gering\",\n"
            "\"sem_einschaetzung\": \"...\",\n"
            "\"sem_empfehlung\": \"...\"\n"
            "}\n```\n\n"
            "Text:  + text + "
        )

        gpt_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Du bist eine freundliche, klare und hilfreiche GPT-Analyse für Datenschutz und digitale Kommunikation."
                },
                {
                    "role": "user",
                    "content": gpt_prompt
                }
            ],
            temperature=0.6
        )
        return jsonify({
            "gpt_raw": gpt_response['choices'][0]['message']['content']
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)