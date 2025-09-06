from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def reply_whatsapp():
    incoming_msg = request.values.get("Body", "").strip().lower()
    response = MessagingResponse()
    msg = response.message()

    # Respond to "hi" or similar
    if incoming_msg in ['hi', 'hello', 'hey']:
        msg.body("👋 Hello! Welcome to our service. How can I help you today?")
    else:
        msg.body("😊 Welcome! Feel free to ask me anything.")

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)
