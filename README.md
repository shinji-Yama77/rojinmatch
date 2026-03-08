# Rojin — Senior Companion Platform

> Hackathon MVP · 4-hour build

## Problem

Customer service lines are flooded by elderly callers seeking connection, not service. Rojin gives them a dedicated phone line where they can talk to a peer — monitored quietly in the background by a caretaker.

---

## What It Does (Scope)

1. Senior calls a Twilio number
2. IVR greets them by name (CallerID lookup), puts them in a queue
3. When two callers are waiting, they get bridged into a Twilio Conference
4. Deepgram transcribes the call in real time
5. A simple web dashboard shows the caretaker a live transcript and flags distress keywords in red

That's it. No app, no login, no typing required for the senior.

---

## Architecture

```
Senior calls → Twilio IVR → FastAPI webhook
                                  ↓
                         CallerID lookup (SQLite)
                                  ↓
                         Matchmaking queue (in-memory)
                                  ↓ (match found)
                         Twilio Conference bridge
                                  ↓
                         Twilio Media Stream → Deepgram ASR
                                  ↓
                         Safety keyword scan
                                  ↓
                         WebSocket push → Caretaker Dashboard (React)
```

---

## Stack

| Piece     | Tech                                      | Why                                    |
| --------- | ----------------------------------------- | -------------------------------------- |
| Telephony | Twilio (IVR + Conference + Media Streams) | PSTN-native, no app needed             |
| Backend   | FastAPI (Python)                          | Fast to write, async WebSocket support |
| ASR       | Deepgram streaming                        | ~300 ms latency, word-level results    |
| DB        | SQLite                                    | Zero setup for a hackathon             |
| Queue     | Python dict in memory                     | Simple enough for demo scale           |
| Dashboard | Single HTML file + vanilla JS             | No build step                          |
| Tunnel    | ngrok                                     | Expose localhost to Twilio webhooks    |

---

## Data Model (3 tables)

**`seniors`** — `phone_e164`, `display_name`, `caretaker_name`

**`sessions`** — `id`, `started_at`, `ended_at`, `participant_phones`

**`transcripts`** — `session_id`, `speaker_phone`, `text`, `flagged` (bool), `ts`

---

## API (5 endpoints)

| Method | Path                | Description                                                  |
| ------ | ------------------- | ------------------------------------------------------------ |
| `POST` | `/webhooks/inbound` | Twilio calls this on new inbound call; returns TwiML         |
| `POST` | `/webhooks/status`  | Twilio call status updates                                   |
| `POST` | `/webhooks/stream`  | Deepgram transcript segments → keyword scan → WebSocket push |
| `GET`  | `/sessions`         | List active sessions (dashboard polling fallback)            |
| `WS`   | `/ws/dashboard`     | Push transcript segments and alerts to caretaker UI          |

---

## Setup and Running the Backend

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the development server:
   ```bash
   uvicorn src.main:app --reload
   ```

---

## Build Order (4 hours)

| Time      | Task                                                                   |
| --------- | ---------------------------------------------------------------------- |
| 0:00–0:30 | Twilio account setup, buy number, ngrok tunnel, FastAPI skeleton       |
| 0:30–1:15 | `/webhooks/inbound` TwiML + in-memory queue + Conference bridge        |
| 1:15–2:00 | Twilio Media Stream → Deepgram WebSocket → transcript storage          |
| 2:00–2:30 | Keyword scan + WebSocket push to dashboard                             |
| 2:30–3:15 | Caretaker dashboard HTML: live transcript list, alerts highlighted red |
| 3:15–3:45 | Seed 2–3 test seniors in SQLite, end-to-end demo call                  |
| 3:45–4:00 | Polish, record demo video                                              |

---

## Key Decisions

- **Twilio Conference** — no WebRTC, no SFU, works on any phone out of the box
- **CallerID = identity** — no passwords, no signup flow for seniors
- **SQLite** — zero ops, fine for a demo with <10 concurrent calls
- **In-memory queue** — a Python list is enough; persistence not needed for hackathon
- **No automated alerts** — dashboard highlights flagged lines in red; caretaker decides what to do
- **Single HTML file dashboard** — no React build step, ships instantly
