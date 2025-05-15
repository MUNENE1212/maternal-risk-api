# app/services/sms_sender.py

import africastalking
from decouple import config

username = config("AFRICASTALKING_USERNAME")  # e.g. "sandbox"
api_key = config("AFRICASTALKING_API_KEY")

africastalking.initialize(username, api_key)
sms = africastalking.SMS

def send_sms(message: str, recipients: list):
    try:
        response = sms.send(message, recipients)
        print(f"SMS sent: {response}")
        return response
    except Exception as e:
        print(f"SMS sending failed: {str(e)}")
        return None

