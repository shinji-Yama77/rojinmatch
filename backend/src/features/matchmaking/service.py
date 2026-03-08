import asyncio
from typing import List, Optional, Tuple
from src.core.websocket import manager

class MatchmakingQueue:
    def __init__(self):
        self.queue: List[dict] = []  # Simple FIFO queue for now

    async def add_caller(self, caller_id: int, phone_number: str):
        caller = {"id": caller_id, "phone_number": phone_number}
        self.queue.append(caller)
        await manager.broadcast({"event": "queue_update", "count": len(self.queue), "caller": caller})
        print(f"Added caller {phone_number} to queue. Queue size: {len(self.queue)}")
        
        # Try to match immediately
        await self.try_match()

    async def try_match(self):
        if len(self.queue) >= 2:
            caller1 = self.queue.pop(0)
            caller2 = self.queue.pop(0)
            
            match_data = {
                "event": "match_found",
                "caller1": caller1,
                "caller2": caller2,
                "status": "connecting_conference"
            }
            await manager.broadcast(match_data)
            print(f"Match found: {caller1['phone_number']} <-> {caller2['phone_number']}")
            
            # Mock connecting to Twilio Conference
            await self.mock_conference_bridge(caller1, caller2)

    async def mock_conference_bridge(self, caller1, caller2):
        # Simulate connecting to Twilio
        await asyncio.sleep(2)
        await manager.broadcast({
            "event": "conference_started",
            "participants": [caller1['phone_number'], caller2['phone_number']],
            "conference_sid": "CF12345mock"
        })
        
        # Start mock streaming/safety scan for this session
        from src.features.safety.service import safety_monitor
        asyncio.create_task(safety_monitor.start_monitoring(caller1, caller2))

match_queue = MatchmakingQueue()
