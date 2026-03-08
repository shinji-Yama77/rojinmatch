import random
from pydantic import BaseModel

class TwilioService:
    def __init__(self, mock: bool = True):
        self.mock = mock

    def incoming_call(self, from_number: str):
        if self.mock:
            return f"Mocked call from {from_number}"
        return "Real Twilio not implemented yet"

    def play_message(self, message: str):
        return f"<Response><Say>{message}</Say></Response>"

twilio_service = TwilioService()
