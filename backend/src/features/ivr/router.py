from fastapi import APIRouter, Request, Form, BackgroundTasks
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
    # In a real app, this might be handled via task queue (Celery/RQ)
    asyncio.create_task(match_queue.add_caller(caller_id, From))

    # 3. Return TwiML
    return twilio_service.play_message("Welcome to RojinMatch. Please wait while we connect you to a partner.")
