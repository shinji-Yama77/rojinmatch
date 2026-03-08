import asyncio
from typing import List, Optional, Tuple
from src.core.websocket import manager
from src.services.twilio import twilio_service

class MatchmakingQueue:
    def __init__(self):
        self.queue: List[dict] = []  # Simple FIFO queue for now

    async def add_caller(self, caller_id: int, phone_number: str, call_sid: str):
        caller = {"id": caller_id, "phone_number": phone_number, "call_sid": call_sid}
        self.queue.append(caller)
        await manager.broadcast({"event": "queue_update", "count": len(self.queue), "caller": caller})
        print(f"Added caller {phone_number} ({call_sid}) to queue. Queue size: {len(self.queue)}")
        
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
            
            # Connect both to a Twilio Conference
            conference_name = f"room_{caller1['id']}_{caller2['id']}"
            await self.connect_to_conference(caller1, caller2, conference_name)

    async def connect_to_conference(self, caller1, caller2, conference_name):
        # In a real async environment, these might be blocking if not careful, 
        # but Twilio API calls are usually fast enough or should be run in executor if needed.
        # Since we are using standard Twilio client (sync), we should probably run it in a thread 
        # if we want to be strictly async, but for MVP direct call is okay or wrap in asyncio.to_thread
        
        print(f"Bridging calls to conference: {conference_name}")
        
        # Connect Caller 1
        success1 = await asyncio.to_thread(twilio_service.connect_to_conference, caller1['call_sid'], conference_name)
        
        # Connect Caller 2
        success2 = await asyncio.to_thread(twilio_service.connect_to_conference, caller2['call_sid'], conference_name)

        if success1 and success2:
            await manager.broadcast({
                "event": "conference_started",
                "participants": [caller1['phone_number'], caller2['phone_number']],
                "conference_sid": conference_name
            })
            
            # Start mock streaming/safety scan for this session
            from src.features.safety.service import safety_monitor
            asyncio.create_task(safety_monitor.start_monitoring(caller1, caller2))
        else:
            print("Failed to bridge calls")
            await manager.broadcast({"event": "error", "message": "Failed to bridge calls"})

match_queue = MatchmakingQueue()
