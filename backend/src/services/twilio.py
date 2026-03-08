import random
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Dial, Conference
from src.config import settings

class TwilioService:
    def __init__(self):
        self.mock = settings.MOCK_TWILIO
        if not self.mock:
            if settings.TWILIO_API_KEY_SID and settings.TWILIO_API_KEY_SECRET:
                self.client = Client(settings.TWILIO_API_KEY_SID, settings.TWILIO_API_KEY_SECRET, settings.TWILIO_ACCOUNT_SID)
            else:
                self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            self.from_number = settings.TWILIO_PHONE_NUMBER

    def get_voice_response(self):
        return VoiceResponse()

    def incoming_call_response(self):
        """Initial response when a user calls: Welcome + Enqueue logic (simulated by waiting music)"""
        resp = VoiceResponse()
        resp.say("Welcome to Rojin Match. Please wait while we find you a partner.")
        # Play hold music loop or just pause
        # In a real app, you might use <Enqueue> but for simplicity we'll just keep the call alive
        resp.play("http://com.twilio.sounds.music.s3.amazonaws.com/MARKOVICHAMP-Borghestral.mp3", loop=10)
        return str(resp)

    def connect_to_conference(self, call_sid: str, conference_name: str):
        """
        Redirect a live call to a conference room.
        """
        if self.mock:
            print(f"MOCK: Connecting {call_sid} to conference {conference_name}")
            return True

        try:
            # Create TwiML to dial the conference
            resp = VoiceResponse()
            dial = Dial()
            dial.conference(conference_name, 
                            start_conference_on_enter=True, 
                            end_conference_on_exit=True)
            resp.append(dial)
            
            # Update the live call with this TwiML
            call = self.client.calls(call_sid).update(twiml=str(resp))
            print(f"Redirected call {call_sid} to conference {conference_name}: {call.status}")
            return True
        except Exception as e:
            print(f"Error connecting to conference: {e}")
            return False

twilio_service = TwilioService()
