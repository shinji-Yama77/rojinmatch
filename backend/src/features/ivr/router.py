from fastapi import APIRouter, Request, Form, BackgroundTasks, Response
from src.features.matchmaking.service import match_queue
from src.core.database import database, callers
from src.services.twilio import twilio_service
import asyncio

router = APIRouter()

@router.post("/incoming")
async def handle_incoming_call(From: str = Form(...), CallSid: str = Form(...)):
    """
    Twilio webhook for incoming calls.
    """
    print(f"Incoming call from {From}, CallSid: {CallSid}")
    
    # 1. CallerID Lookup (SQLite)
    query = callers.select().where(callers.c.phone_number == From)
    caller = await database.fetch_one(query)
    
    if not caller:
        # Create a new caller if not exists (Mock behavior)
        query = callers.insert().values(phone_number=From, name=f"Caller {From[-4:]}", is_senior=True)
        caller_id = await database.execute(query)
        print(f"New caller created: {caller_id}")
    else:
        caller_id = caller.id
        print(f"Existing caller found: {caller.name}")

    # 2. Add to Matchmaking Queue (Background Task to not block Twilio response)
    asyncio.create_task(match_queue.add_caller(caller_id, From, CallSid))

    # 3. Return TwiML (Wait/Enqueue)
    twiml_response = twilio_service.incoming_call_response()
    return Response(content=twiml_response, media_type="application/xml")
