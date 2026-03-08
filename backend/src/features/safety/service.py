import asyncio
import random
from src.core.websocket import manager
from src.services.shisa import shisa_service

class SafetyMonitor:
    def __init__(self):
        self.mock_transcripts = [
            "こんにちは、お元気ですか？", # Hello, how are you?
            "はい、元気です。", # Yes, I'm fine.
            "犬を飼っています。", # I have a dog.
            "それはいいですね。私は猫派です。", # That's nice. I'm a cat person.
            "ちょっと怖い。", # Wait, I'm scared.
            "助けて！", # Help me!
            "銀行でお金をおろしましょう。", # Let's withdraw money at the bank.
            "詐欺に注意してください。", # Please be careful of scams.
            "Hello, how are you?",
            "I feel unsafe.",
            "Let's meet at the bank."
        ]
        # self.unsafe_keywords removed, delegated to ShisaService

    async def start_monitoring(self, caller1: dict, caller2: dict):
        """Simulate a streaming connection and safety scan using Shisa AI."""
        print(f"Starting safety monitoring for {caller1['phone_number']} and {caller2['phone_number']}")
        
        # Simulate conversation duration
        for _ in range(10):  # 10 mock exchanges
            await asyncio.sleep(2)
            
            transcript = random.choice(self.mock_transcripts)
            speaker = random.choice([caller1['phone_number'], caller2['phone_number']])
            
            # Check for safety using Shisa AI
            is_safe = await shisa_service.check_safety(transcript)
            is_unsafe = not is_safe
            
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
                    "message": f"Unsafe content detected by Shisa AI: {transcript}",
                    "context": payload
                })

safety_monitor = SafetyMonitor()
