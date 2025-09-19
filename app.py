import os
import smtplib
from email.message import EmailMessage
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load env vars
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
BACKEND_API_KEY = os.getenv("BACKEND_API_KEY")

if not all([EMAIL_USER, EMAIL_APP_PASSWORD, BACKEND_API_KEY]):
    raise RuntimeError("Missing required environment variables")

app = Flask(__name__)

def send_email(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_USER, EMAIL_APP_PASSWORD)
        smtp.send_message(msg)

@app.route("/send-email", methods=["POST"])
def send_email_route():
    # Simple authentication
    api_key = request.headers.get("X-API-KEY")
    if api_key != BACKEND_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    if not data or not all(k in data for k in ("to_email", "subject", "text")):
        return jsonify({"error": "Missing fields"}), 400

    try:
        send_email(data["to_email"], data["subject"], data["text"])
        return jsonify({"status": "sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
