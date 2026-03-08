import asyncio
import random
from src.core.websocket import manager

class SafetyMonitor:
    def __init__(self):
        self.mock_transcripts = [
            "Hello, how are you?",
            "I'm fine, thank you.",
            "I have a dog named Rover.",
            "Oh, that's nice. I used to have a cat.",
            "Wait, I feel unsafe.",
            "Help me!",
            "Let's meet at the bank.",  # Potential unsafe keyword
            "Scam alert!"
        ]
        self.unsafe_keywords = ["unsafe", "help", "bank", "money", "scam"]

    async def start_monitoring(self, caller1: dict, caller2: dict):
        """Simulate a streaming connection and safety scan."""
        print(f"Starting safety monitoring for {caller1['phone_number']} and {caller2['phone_number']}")
        
        # Simulate conversation duration
        for _ in range(10):  # 10 mock exchanges
            await asyncio.sleep(2)
            
            transcript = random.choice(self.mock_transcripts)
            speaker = random.choice([caller1['phone_number'], caller2['phone_number']])
            
            # Check for unsafe keywords
            is_unsafe = any(keyword in transcript.lower() for keyword in self.unsafe_keywords)
            
            payload = {
                "event": "transcript",
                "speaker": speaker,
                "text": transcript,
                "is_unsafe": is_unsafe,
                "conference_sid": "CF12345mock"
            }
            
            await manager.broadcast(payload)
            
            if is_unsafe:
                await manager.broadcast({
                    "event": "alert",
                    "severity": "high",
                    "message": f"Unsafe keyword detected: {transcript}",
                    "context": payload
                })

safety_monitor = SafetyMonitor()
