import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv() # Load keys from .env file

# Get these from your Twilio Dashboard
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")
TARGET_PHONE = os.getenv("TARGET_PHONE") # Your phone number

def send_sms_alert(message_body):
    """
    Sends an SMS to the target phone number using Twilio.
    """
    if not TWILIO_SID or not TWILIO_AUTH:
        print("⚠️ Twilio credentials missing in .env file! Skipping SMS.")
        return

    try:
        client = Client(TWILIO_SID, TWILIO_AUTH)
        
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE,
            to=TARGET_PHONE
        )
        print(f"✅ SMS Sent! SID: {message.sid}")
    except Exception as e:
        print(f"❌ SMS Failed: {e}")