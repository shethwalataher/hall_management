import os
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
        msg.body("Hello! Welcome to Hall Booking System of Tayebi Mohallah(Mumbai).")
    else:
        msg.body("Welcome to Hall Booking System of Tayebi Mohallah(Mumbai).")

    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's dynamic port
    app.run(host="0.0.0.0", port=port, debug=True)


