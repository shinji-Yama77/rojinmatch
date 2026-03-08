import asyncio
import json

from fastapi import APIRouter, Form, Response, WebSocket, WebSocketDisconnect

from src.core.database import database, callers
from src.features.matchmaking.service import match_queue
from src.services.twilio import twilio_service

router = APIRouter()


@router.post("/incoming")
async def handle_incoming_call(From: str = Form(...), CallSid: str = Form(...)):
    """Twilio webhook — fires when a senior calls in."""
    print(f"Incoming call from {From}, CallSid: {CallSid}")

    query = callers.select().where(callers.c.phone_number == From)
    caller = await database.fetch_one(query)

    if not caller:
        query = callers.insert().values(phone_number=From, name=f"Caller {From[-4:]}", is_senior=True)
        caller_id = await database.execute(query)
        print(f"New caller registered: {caller_id}")
    else:
        caller_id = caller.id
        print(f"Known caller: {caller.name}")

    asyncio.create_task(match_queue.add_caller(caller_id, From, CallSid))

    twiml = twilio_service.incoming_call_response()
    return Response(content=twiml, media_type="application/xml")


@router.websocket("/stream")
async def media_stream(websocket: WebSocket):
    """
    Twilio Media Streams endpoint.
    Receives raw mulaw audio, forwards to Deepgram, pushes transcripts to dashboard.
    """
    await websocket.accept()

    call_sid = "unknown"
    phone_number = "unknown"

    try:
        for _ in range(2):
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            if msg.get("event") == "start":
                call_sid = msg["start"]["callSid"]
                params = msg["start"].get("customParameters", {})
                phone_number = params.get("from", call_sid[-4:])
                break

        print(f"Media stream started: {phone_number} ({call_sid})")

        from src.services.deepgram import bridge_twilio_to_deepgram
        await bridge_twilio_to_deepgram(websocket, call_sid, phone_number)

    except WebSocketDisconnect:
        print(f"Media stream disconnected: {phone_number}")
    except Exception as e:
        print(f"Media stream error: {e}")
