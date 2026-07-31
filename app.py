import speech_recognition as sr
from flask import Flask, jsonify, request
from flask_cors import CORS  # <-- CORS import panni irukkom

app = Flask(__name__)
CORS(app)  # <-- Web browser request-a allow panna ithu mukkiyam

# Sample In-Memory Databases
customers = []
agents = [{"id": 1, "name": "Agent A", "workload": 0}]
tickets = []
surveys = []
@app.route("/")
def home():
    return "CRM Backend API is running successfully!"

def classify_ticket(description):
    desc = description.lower()
    if any(word in desc for word in ["payment", "money", "failed", "refund"]):
        return "Billing Issue"
    elif any(
        word in desc for word in ["app", "crash", "error", "slow", "bug"]
    ):
        return "Technical Issue"
    elif any(word in desc for word in ["delivery", "late", "order"]):
        return "Logistics Issue"
    else:
        return "General Query"

@app.route("/chatbot", methods=["POST"])
def chatbot_support():
    data = request.json or {}
    user_message = data.get("message", "").lower()

    if "refund" in user_message:
        reply = "Refunds take 5-7 business days to process."
    elif "working hours" in user_message:
        reply = "Our support agents are available 24/7!"
    else:
        reply = "I'm not sure about that. Would you like to create a ticket for an agent?"

    return jsonify({"bot_response": reply})

@app.route("/voice-ticket", methods=["POST"])
def voice_ticket():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            text_transcript = recognizer.recognize_google(audio_data)

        # Auto-create ticket from converted text
        category = classify_ticket(text_transcript)
        ticket = {
            "ticket_id": len(tickets) + 1,
            "issue": text_transcript,
            "category": category,
            "status": "Open",
            "source": "Voice",
        }
        tickets.append(ticket)

        return (
            jsonify(
                {
                    "message": "Voice ticket created successfully!",
                    "transcribed_text": text_transcript,
                    "ticket": ticket,
                }
            ),
            201,
        )
    except Exception as e:
        return (
            jsonify({"error": "Failed to process audio", "details": str(e)}),
            500,
        )

# Customer Management
@app.route("/customer", methods=["POST"])
def add_customer():
    data = request.json or {}
    customer = {
        "id": len(customers) + 1,
        "name": data.get("name", "Unknown"),
        "email": data.get("email", ""),
    }
    customers.append(customer)
    return jsonify(customer), 201


# Ticket Management with Auto Classification & Agent Assignment
@app.route("/ticket", methods=["POST"])
def create_ticket():
    data = request.json or {}
    issue = data.get("issue", "")

    if not issue:
        return jsonify({"error": "Issue description is required"}), 400

    # AI Classification
    category = classify_ticket(issue)

    # Assign Agent with least workload
    agent = min(agents, key=lambda x: x["workload"])
    agent["workload"] += 1

    ticket = {
        "ticket_id": len(tickets) + 1,
        "customer_id": data.get("customer_id", 1),
        "issue": issue,
        "category": category,
        "priority": data.get("priority", "Low"),
        "status": "Open",
        "assigned_agent": agent["name"],
    }
    tickets.append(ticket)
    return jsonify(ticket), 201


# CSAT & Feedback System
@app.route("/survey", methods=["POST"])
def submit_survey():
    data = request.json or {}
    survey = {
        "survey_id": len(surveys) + 1,
        "ticket_id": data.get("ticket_id"),
        "rating": data.get("rating", 5),  # Scale 1 to 5
        "feedback": data.get("feedback", ""),
    }
    surveys.append(survey)
    return jsonify({"message": "Thank you for the feedback!", "survey": survey})

@app.route("/dashboard", methods=["GET"])
def dashboard():
    total = len(tickets)
    pending = sum(1 for t in tickets if t["status"] == "Open")
    resolved = sum(1 for t in tickets if t["status"] == "Closed")

    # CSAT Calculation
    total_ratings = sum(s["rating"] for s in surveys)
    csat = (
        (total_ratings / (len(surveys) * 5)) * 100 if len(surveys) > 0 else 0
    )

    return jsonify(
        {
            "total_tickets": total,
            "pending_tickets": pending,
            "resolved_tickets": resolved,
            "csat_score": f"{round(csat, 2)}%",
        }
    )


if __name__ == "__main__":
    app.run(debug=True)