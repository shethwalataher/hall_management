import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime

app = Flask(__name__)

# Session data: phone number => session info
# Supports multiple bookings
session_store = {}

@app.route("/whatsapp", methods=["POST"])
def reply_whatsapp():
    incoming_msg = request.values.get("Body", "").strip()
    user_number = request.values.get("From", "")  # e.g., 'whatsapp:+911234567890'

    response = MessagingResponse()
    msg = response.message()

    # Initialize user session if not exists
    if user_number not in session_store:
        session_store[user_number] = {
            'current_booking': {},
            'bookings': []
        }

    user_session = session_store[user_number]
    current_booking = user_session['current_booking']

    # Step 1: Greeting / Restart
    if incoming_msg.lower() in ['hi', 'hello', 'hey'] or not current_booking:
        msg.body("👋 Hello! Welcome to the Hall Booking System of Tayebi Mohallah (Mumbai).\n\nHow many thaals do you want to book?")
        user_session['current_booking'] = {'step': 'awaiting_thaals'}

    # Step 2: Get number of thaals
    elif current_booking.get('step') == 'awaiting_thaals':
        if incoming_msg.isdigit():
            current_booking['thaals'] = int(incoming_msg)
            current_booking['step'] = 'awaiting_date'
            msg.body("📅 Great! Please enter the **date of the event** in `YYYY-MM-DD` format.")
        else:
            msg.body("⚠️ Please enter a valid number of thaals (e.g., 1, 2, 3).")

    # Step 3: Get event date
    elif current_booking.get('step') == 'awaiting_date':
        try:
            datetime.strptime(incoming_msg, "%Y-%m-%d")  # validate format
            current_booking['date'] = incoming_msg
            current_booking['step'] = 'awaiting_time'
            msg.body("🕒 Noted! Is your event during the **Day** or **Night**?")
        except ValueError:
            msg.body("⚠️ Please enter the date in correct `YYYY-MM-DD` format (e.g., 2025-09-10).")

    # Step 4: Get Day/Night
    elif current_booking.get('step') == 'awaiting_time':
        if incoming_msg.lower() in ['day', 'night']:
            current_booking['time'] = incoming_msg.capitalize()

            # Booking complete — move it to bookings list
            booking_summary = {
                'thaals': current_booking['thaals'],
                'date': current_booking['date'],
                'time': current_booking['time']
            }
            user_session['bookings'].append(booking_summary)
            user_session['current_booking'] = {}  # reset for next booking

            msg.body(
                f"✅ *Booking Summary:*\n"
                f"- Thaals: {booking_summary['thaals']}\n"
                f"- Date: {booking_summary['date']}\n"
                f"- Time: {booking_summary['time']}\n\n"
                f"Thank you! To make another booking, type 'hi'."
            )

            # TODO: Optionally save booking to file or database here

        else:
            msg.body("⚠️ Please reply with either `Day` or `Night`.")

    else:
        msg.body("Welcome to the Hall Booking System.\nPlease type 'hi' to start your booking.")

    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
