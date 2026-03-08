import asyncio
import base64
import json

import websockets
from fastapi import WebSocket
from src.config import settings
from src.core.websocket import manager

DISTRESS_KEYWORDS = {
    "help",
    "hurt",
    "pain",
    "fall",
    "fallen",
    "alone",
    "scared",
    "chest",
    "breathe",
    "emergency",
    "unsafe",
    "scam",
    "money",
    "bank",
    "afraid",
    "dying",
}

DEEPGRAM_URL = (
    "wss://api.deepgram.com/v1/listen"
    "?encoding=mulaw"
    "&sample_rate=8000"
    "&model=nova-2"
    "&punctuate=true"
    "&interim_results=false"
)


async def bridge_twilio_to_deepgram(
    twilio_ws: WebSocket, call_sid: str, phone_number: str
):
    headers = {"Authorization": f"Token {settings.DEEPGRAM_API_KEY}"}

    async with websockets.connect(DEEPGRAM_URL, additional_headers=headers) as dg_ws:

        async def receive_transcripts():
            async for raw in dg_ws:
                data = json.loads(raw)
                if data.get("type") != "Results":
                    continue
                transcript = data["channel"]["alternatives"][0]["transcript"].strip()
                if not transcript:
                    continue

                is_flagged = any(kw in transcript.lower() for kw in DISTRESS_KEYWORDS)
                payload = {
                    "event": "transcript",
                    "speaker": phone_number,
                    "text": transcript,
                    "is_unsafe": is_flagged,
                    "call_sid": call_sid,
                }
                await manager.broadcast(payload)

                if is_flagged:
                    await manager.broadcast(
                        {
                            "event": "alert",
                            "severity": "high",
                            "message": f"Distress detected: {transcript}",
                            "context": payload,
                        }
                    )

        transcript_task = asyncio.create_task(receive_transcripts())

        try:
            while True:
                raw = await twilio_ws.receive_text()
                msg = json.loads(raw)

                if msg["event"] == "media":
                    audio_bytes = base64.b64decode(msg["media"]["payload"])
                    await dg_ws.send(audio_bytes)
                elif msg["event"] == "stop":
                    break

        except Exception as e:
            print(f"Media stream error ({phone_number}): {e}")
        finally:
            transcript_task.cancel()
            await dg_ws.close()
