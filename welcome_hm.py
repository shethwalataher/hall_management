import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime

app = Flask(__name__)

# In-memory session store (for development/testing)
session_store = {}

@app.route("/whatsapp", methods=["POST"])
def reply_whatsapp():
    incoming_msg = request.values.get("Body", "").strip()
    user_number = request.values.get("From", "")  # e.g., 'whatsapp:+911234567890'

    response = MessagingResponse()
    msg = response.message()

    # Get user session state
    user_state = session_store.get(user_number, {})

    # Step 1: Initial greeting
    if incoming_msg.lower() in ['hi', 'hello', 'hey'] and not user_state:
        msg.body("👋 Hello! Welcome to the Hall Booking System of Tayebi Mohallah (Mumbai).\n\nHow many thaals do you want to book?")
        session_store[user_number] = {'step': 'awaiting_thaals'}

    # Step 2: Get number of thaals
    elif user_state.get('step') == 'awaiting_thaals':
        if incoming_msg.isdigit():
            thaals = int(incoming_msg)
            session_store[user_number] = {
                'step': 'awaiting_date',
                'thaals': thaals
            }
            msg.body("📅 Great! Please enter the **date of the event** in `YYYY-MM-DD` format.")
        else:
            msg.body("⚠️ Please enter a valid number of thaals (e.g., 1, 2, 3).")

    # Step 3: Get event date
    elif user_state.get('step') == 'awaiting_date':
        try:
            # Validate date format
            datetime.strptime(incoming_msg, "%Y-%m-%d")
            session_store[user_number]['date'] = incoming_msg
            session_store[user_number]['step'] = 'awaiting_time'
            msg.body("🕒 Noted! Is your event during the **Day** or **Night**?")
        except ValueError:
            msg.body("⚠️ Please enter the date in correct `YYYY-MM-DD` format (e.g., 2025-09-10).")

    # Step 4: Get Day/Night
    elif user_state.get('step') == 'awaiting_time':
        if incoming_msg.lower() in ['day', 'night']:
            session_store[user_number]['time'] = incoming_msg.capitalize()
            session_store[user_number]['step'] = 'completed'

            # Final summary
            thaals = session_store[user_number]['thaals']
            date = session_store[user_number]['date']
            time = session_store[user_number]['time']

            msg.body(
                f"✅ *Booking Summary:*\n"
                f"- Thaals: {thaals}\n"
                f"- Date: {date}\n"
                f"- Time: {time}\n\n"
                f"Thank you! We’ll follow up with confirmation."
            )

            # TODO: Save booking to database or file here

        else:
            msg.body("⚠️ Please reply with either `Day` or `Night`.")

    # Already completed
    # elif user_state.get('step') == 'completed':
       # msg.body("✅ Your booking has already been recorded. If you want to make a new booking, please type 'hi'.")

    # Unknown flow
    else:
        msg.body("Welcome to the Hall Booking System of Tayebi Mohallah (Mumbai).\nPlease type 'hi' to start your booking.")

    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
