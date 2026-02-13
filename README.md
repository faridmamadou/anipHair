# Anip Hair 💇‍♀️

Hair salon management system with a WhatsApp bot that understands voice messages.

---

## What it does

- **Appointments**: Clients can book, check, and cancel appointments from the web or directly via WhatsApp
- **Voice messages**: The bot automatically transcribes voice notes using Groq Whisper
- **Natural understanding**: Powered by Llama-3, the bot understands requests in plain language ("I want an appointment tomorrow morning")
- **Schedule management**: Automatic calculation of available slots and conflict detection
- **Native WhatsApp**: Bidirectional communication via Baileys (no need for the official API)

---

## Architecture

The project runs in 3 parts:
```
Frontend (React + Vite)  →  API (FastAPI + Python)  ←  WhatsApp Bot (Node.js + Baileys)
```

- **Frontend**: Web interface for the salon admin
- **Backend**: Handles the DB (SQLite), appointments, and talks to Groq for AI
- **WhatsApp Bot**: Listens to messages, sends audio to backend for transcription

---

## Running the project

### With Docker (recommended)

**Prerequisites:**
- Docker installed
- A Groq API key (free at [console.groq.com](https://console.groq.com/))

**Setup:**

1. Create `backend/.env`:
```env
GROQ_API_KEY=gsk_xxxxx
ADMIN_PHONE_NUMBER=229XXXXXXXX
```

2. Launch everything:
```bash
docker compose up --build
```

3. First launch → Scan the WhatsApp QR code in the bot logs

4. Access:
   - Web interface: http://localhost:5173
   - API: http://localhost:8000

---

## Local development

If you prefer dev without Docker:

**Backend:**
```bash
cd backend
uv sync
uv run uvicorn main:app --reload
```

**WhatsApp Bot:**
```bash
cd backend/node
npm install
npm start
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## Test audio transcription
```bash
cd backend
uv run python3 tests/test_audio_transcription.py
```

---

## Notes

- WhatsApp session is saved in a Docker volume (no need to rescan on each restart)
- Audio files are never written to disk, everything happens in memory
- SQLite DB is also in a Docker volume to persist data

---

## License

Private project.