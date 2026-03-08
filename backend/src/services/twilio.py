from src.config import settings
from twilio.rest import Client
from twilio.twiml.voice_response import Conference, Dial, Start, Stream, VoiceResponse


class TwilioService:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.from_number = settings.TWILIO_PHONE_NUMBER

    def incoming_call_response(self):
        resp = VoiceResponse()
        resp.say("Welcome to Rojin Match. Please wait while we find you a partner.")
        resp.play(
            "http://com.twilio.sounds.music.s3.amazonaws.com/MARKOVICHAMP-Borghestral.mp3",
            loop=0,
        )
        return str(resp)

    def connect_to_conference(self, call_sid: str, conference_name: str):
        try:
            resp = VoiceResponse()

            # Start streaming audio to Deepgram via our WebSocket endpoint
            stream_url = settings.SERVER_URL.replace("http://", "wss://").replace("https://", "wss://")
            start = Start()
            start.stream(url=f"{stream_url}/api/ivr/stream")
            resp.append(start)

            dial = Dial()
            dial.conference(
                conference_name,
                start_conference_on_enter=True,
                end_conference_on_exit=True,
            )
            resp.append(dial)

            call = self.client.calls(call_sid).update(twiml=str(resp))
            print(f"Redirected {call_sid} to {conference_name}: {call.status}")
            return True
        except Exception as e:
            print(f"Error connecting to conference: {e}")
            return False


twilio_service = TwilioService()
