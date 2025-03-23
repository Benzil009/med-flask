import os
import sys
from aixplain.factories import ModelFactory
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Fix Unicode printing issue in Windows
sys.stdout.reconfigure(encoding='utf-8')

# Set Aixplain API Key
os.environ["AIXPLAIN_API_KEY"] = "09177c14cce0b5bf4a6198438dd2b1fc8eb7f119a38a7fecb327ce2f074c72eb"

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# Load the Aixplain Model
MODEL_ID = "6759db476eb56303857a07c1"
try:
    model = ModelFactory.get(MODEL_ID)
    print("✅ Aixplain model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None  # Prevent crashes if model fails to load

def classify_query(user_message):
    """Classifies the query as 'Medical' or 'Non-Medical'. Returns True if Medical, otherwise False."""
    if not model:
        print("⚠ Model not loaded. Defaulting to Non-Medical.")
        return False  

    # Force model to return only 'Medical' or 'Non-Medical'
    classification_prompt = (
        f"Classify this query strictly as 'Medical' or 'Non-Medical'. "
        f"Reply with ONLY 'Medical' or 'Non-Medical'. Query: {user_message}"
    )

    try:
        result = model.run({"text": classification_prompt})
        response_text = result.get("data", "") or result.get("text", "")
        response_text = str(response_text).strip()

        print(f"🔎 Model classification response: '{response_text}'")

        return response_text.lower() == "medical"
    
    except Exception as e:
        print(f"⚠ Error in classification: {e}")
        return False  # Default to Non-Medical on failure

def get_ai_response(user_message, language="English"):
    """Fetches AI response if the query is medical."""
    if not model:
        return "Error: AI model is not available."

    # Ensure response language
    language_instruction = f"Respond in {language}. " if language.lower() != "english" else ""

    # Formulate the AI response prompt
    prompt = f"{language_instruction}{user_message} Provide the response in a numbered list with 5 clear and short points."

    print(f"📨 Prompt sent to model: {prompt}")

    try:
        result = model.run({
        "text": prompt,
        "max_tokens": 256  # Increased from 128 to 256
        })

        response_text = result.get("data", "") or result.get("text", "")

        return response_text or "Sorry, I couldn't process your request."
    
    except Exception as e:
        print(f"⚠ Error getting AI response: {e}")
        return "An error occurred while generating a response."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chatbot_reply():
    """Receives a message from frontend and returns an AI response."""
    data = request.json
    user_message = data.get("message", "")
    language = data.get("language", "English")

    if classify_query(user_message):
        bot_reply = get_ai_response(user_message, language)
    else:
        bot_reply = (
            f"Translate to {language}: This bot only provides medical information. Please ask health-related questions."
            if language.lower() != "english"
            else "This bot only provides medical information. Please ask health-related questions."
        )

    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
