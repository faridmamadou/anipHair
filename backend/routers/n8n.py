from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import Field
from schemas import WhatsAppMessage, WhatsAppAudioMessage
from datetime import datetime
from typing import Dict

router = APIRouter(prefix="/messages", tags=["messages"])

last_messages: Dict[str, Dict] = {}

@router.post("/receive")
async def receive_message(message: WhatsAppMessage):
    last_messages[message.chat_id] = message.dict()
    
    return {"status": "success", "stored_for": message.chat_id}

@router.post("/messages/receive-audio")
async def receive_audio_message(
    audio_msg: WhatsAppAudioMessage,
    background_tasks: BackgroundTasks,
):
    # Ignorer les messages envoyés par le bot lui-même
    if audio_msg.fromMe:
        return {"status": "ignored", "reason": "message from bot"}
    
    
    # Définir le chemin de sauvegarde
    output_dir = "audios"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{audio_msg.message_id.replace('/', '_')}.ogg"
    
    # Télécharger l'audio
    audio_bytes = await service.download_audio_from_url(
        audio_msg.audio_url, 
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