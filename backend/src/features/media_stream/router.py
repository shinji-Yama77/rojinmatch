from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.core.websocket import manager
from src.features.safety.service import safety_monitor
import asyncio
import json

router = APIRouter()

@router.websocket("/ws/media-stream")
async def media_stream_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for Twilio Media Streams.
    Twilio connects here and sends audio chunks.
    We forward audio to Deepgram (or mock it) and receive transcripts.
    """
    await websocket.accept()
    print("Twilio Media Stream connected")
    
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data['event'] == 'start':
                print(f"Stream started: {data['start']['streamSid']}")
                # In a real app, we would start a connection to Deepgram here
                # For now, we rely on the safety_monitor mock started in matchmaking/service.py
                # But if we were doing real-time streaming, we would process audio here:
            elif data['event'] == 'media':
                # payload = data['media']['payload']
                # Decode base64 and send to Deepgram
                pass
            elif data['event'] == 'stop':
                print("Stream stopped")
                break
                
    except WebSocketDisconnect:
        print("Twilio Media Stream disconnected")
    except Exception as e:
        print(f"Media Stream error: {e}")
