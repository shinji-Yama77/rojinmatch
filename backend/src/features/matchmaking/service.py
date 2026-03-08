import asyncio
from typing import List
from src.core.websocket import manager
from src.services.twilio import twilio_service


class MatchmakingQueue:
    def __init__(self):
        self.queue: List[dict] = []

    async def add_caller(self, caller_id: int, phone_number: str, call_sid: str):
        # Don't add if already waiting
        if any(c["phone_number"] == phone_number for c in self.queue):
            return
        caller = {"id": caller_id, "phone_number": phone_number, "call_sid": call_sid}
        self.queue.append(caller)
        await manager.broadcast({"event": "queue_update", "count": len(self.queue)})
        print(f"Queued {phone_number} ({call_sid}). Queue size: {len(self.queue)}")
        await self.try_match()

    async def try_match(self):
        if len(self.queue) < 2:
            return

        caller1 = self.queue.pop(0)
        caller2 = self.queue.pop(0)
        conference_name = f"room_{caller1['id']}_{caller2['id']}"

        print(f"Match: {caller1['phone_number']} <-> {caller2['phone_number']} → {conference_name}")
        await manager.broadcast({
            "event": "match_found",
            "caller1": caller1["phone_number"],
            "caller2": caller2["phone_number"],
            "room": conference_name,
        })

        success1 = await asyncio.to_thread(twilio_service.connect_to_conference, caller1["call_sid"], conference_name)
        success2 = await asyncio.to_thread(twilio_service.connect_to_conference, caller2["call_sid"], conference_name)

        if success1 and success2:
            await manager.broadcast({
                "event": "conference_started",
                "participants": [caller1["phone_number"], caller2["phone_number"]],
                "conference_sid": conference_name,
            })
            # Transcription handled by Deepgram via Twilio Media Streams on /api/ivr/stream
        else:
            print("Failed to bridge calls")
            await manager.broadcast({"event": "error", "message": "Failed to bridge calls"})


match_queue = MatchmakingQueue()
