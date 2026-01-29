from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import Field
from schemas import WhatsAppMessage, WhatsAppAudioMessage
from datetime import datetime
from typing import Dict
from database import get_db
from sqlalchemy.orm import Session
from services.whatsapp_service import WhatsAppSessionService
import os
from config import ADMIN_PHONE_NUMBER

router = APIRouter(prefix="/messages", tags=["messages"])

last_messages: Dict[str, Dict] = {}

@router.post("/receive")
async def receive_message(
    message: WhatsAppMessage,
    db: Session = Depends(get_db)
):
    whatsapp_service = WhatsAppSessionService(db)

    chat_id = ADMIN_PHONE_NUMBER
    text = (message.content or "").upper().strip()
    print(message)
    # --- ROUTING PAR MOT CLÉ ---
    if "LAST" in text:
        response_text = whatsapp_service.get_last_appointment(chat_id)

    elif "TODAY" in text:
        response_text = whatsapp_service.get_today_appointments(chat_id)

    elif "HELP" in text or "AIDE" in text:
        response_text = (
            "🤖 Commandes disponibles :\n"
            "- *LAST*\n"
            "- *TODAY*\n"
            "- *HELP*"
        )

    else:
        response_text = (
            "❓ Je n’ai pas compris votre demande.\n"
            "Tapez *help* pour voir les commandes disponibles."
        )

    # --- ENVOI WHATSAPP ---
    await whatsapp_service.send_message(chat_id, response_text)

    return {
        "status": "success",
        "chat_id": chat_id,
        "matched_text": text,
        "response_text": response_text
    }

@router.post("/receive-audio")
async def receive_audio_message(
    audio_msg: WhatsAppAudioMessage,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Définir le chemin de sauvegarde
    output_dir = "audios"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{audio_msg.message_id.replace('/', '_')}.ogg"
    service = WhatsAppSessionService(db)
    # Télécharger l'audio
    audio_bytes = await service.download_audio  (
        audio_msg.chat_id,
        audio_msg.message_id,
        output_path
    )
    
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Failed to download audio")
    
    # TODO: Ajouter la transcription audio ici
    # from services.transcription_service import transcribe_audio
    # transcription = await transcribe_audio(audio_bytes)
    
    # TODO: Envoyer la transcription au LLM
    # response = await process_with_llm(transcription, audio_msg.chat_id)
    
    # TODO: Répondre sur WhatsApp
    # await service.send_message(audio_msg.chat_id, response)
    
    return {
        "status": "success",
        "message_id": audio_msg.message_id,
        "audio_url": audio_msg.audio_url,
        "saved_to": output_path,
        "timestamp": audio_msg.timestamp
    }