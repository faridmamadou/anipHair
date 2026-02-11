from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Form
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
from services.messages_service import MessagesService
import schemas
import os

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/receive")
async def receive_message(
    request: Request,
    type: str = Form(None),
    sender_id: str = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    service = MessagesService(db)
    
    # Check if it's a JSON request (text message)
    content_type = request.headers.get("Content-Type", "")
    
    if "application/json" in content_type:
        data = await request.json()
        msg_type = data.get("type")
        message = data.get("message")
        sender = data.get("sender_id")
        
        print(f"📩 Message texte reçu de {sender}: {message}")
        
        # Process with service
        reply = await service.process_message(message, sender)
        
        return {
            "status": "success", 
            "received": {"type": msg_type, "message": message, "sender_id": sender},
            "reply": reply
        }

    # Handle Multi-part/Form-Data (audio message)
    if type == "audio" and file:
        file_path = f"audios/received_audio_{sender_id}_{os.urandom(4).hex()}.ogg"
        os.makedirs("audios", exist_ok=True)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        print(f"🎵 Audio reçu de {sender_id}, sauvegardé sous: {file_path}")
        return {
            "status": "success", 
            "received": {"type": "audio", "file": file_path, "sender_id": sender_id},
            "reply": "J'ai bien reçu votre message audio, je l'analyse..."
        }

    raise HTTPException(status_code=400, detail="Invalid request format or type")

@router.get("/status")
async def get_status():
    return {"status": "active"}