from fastapi import APIRouter
from schemas import WhatsAppMessage
from datetime import datetime
from typing import Dict

router = APIRouter(prefix="/messages", tags=["messages"])

last_messages: Dict[str, Dict] = {}

@router.post("/receive")
async def receive_message(message: WhatsAppMessage):
    last_messages[message.chat_id] = message.dict()
    
    return {"status": "success", "stored_for": message.chat_id}


