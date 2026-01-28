import httpx
import os
from sqlalchemy.orm import Session
import models
import schemas
from typing import Optional, Dict, Any
import logging
from dotenv import load_dotenv

from .whatsapp_parser import extract_whatsapp_user_messages

load_dotenv()

WAWP_BASE_URL = os.getenv("WAWP_BASE_URL")
WAWP_API_KEY = os.getenv("WAWP_API_KEY")
WAWP_API_INSTANCE = os.getenv("WAWP_API_INSTANCE")

logger = logging.getLogger(__name__)

class WhatsAppSessionService:
    def __init__(self, db: Session):
        self.db = db
        self.instance_id = WAWP_API_INSTANCE
        self.access_token = WAWP_API_KEY

    async def create_session(self, session_name: str) -> models.WhatsAppSession:
        db_session = self.db.query(models.WhatsAppSession).filter(models.WhatsAppSession.session_name == session_name).first()
        if not db_session:
            db_session = models.WhatsAppSession(session_name=session_name, status="DISCONNECTED")
            self.db.add(db_session)
            self.db.commit()
            self.db.refresh(db_session)
        return db_session

    async def start_session(self) -> dict:
        # Call Wawp API to start/create session
        # Based on Wawp docs (assuming endpoints based on research)
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{WAWP_BASE_URL}/session/start",
                    params={
                        "instance_id": self.instance_id,
                        "access_token": self.access_token
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data
            except httpx.HTTPStatusError as e:
                logger.error(f"Error starting Wawp session: {e.response.text}")
                return {"error": str(e), "detail": e.response.text}
            except Exception as e:
                logger.error(f"Unexpected error starting Wawp session: {e}")
                return {"error": str(e)}

    # async def get_session_status(self, session_name: str) -> Optional[models.WhatsAppSession]:
    #     return self.db.query(models.WhatsAppSession).filter(models.WhatsAppSession.session_name == session_name).first()

    async def stop_session(self) -> bool:

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{WAWP_BASE_URL}/session/logout",
                    params={
                        "instance_id": self.instance_id,
                        "access_token": self.access_token
                    }
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Error stopping Wawp session: {e.response.text}")
                return {"error": str(e), "detail": e.response.text}
            except Exception as e:
                logger.error(f"Unexpected error stopping Wawp session: {e}")
                return {"error": str(e)}

    async def send_message(self, chat_id: str, text: str) -> dict:
        params = {
            "instance_id": self.instance_id,
            "access_token": self.access_token,
            "chatId": chat_id,
            "message": text
        }

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.post(
                    f"{WAWP_BASE_URL}/send",
                    params=params
                )

                # WAWP peut parfois renvoyer un 200 sans body
                if response.status_code == 200 and not response.content:
                    return {"status": "success", "message": "Message sent (empty body)"}

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(
                    f"WAWP HTTP error {e.response.status_code}: {e.response.text}"
                )
                return {
                    "error": "wawp_http_error",
                    "status_code": e.response.status_code,
                    "details": e.response.text
                }

            except Exception as e:
                logger.exception("Unexpected error sending WhatsApp message")
                return {"error": "unexpected_error", "details": str(e)}

            
    
    def parse_incoming_message(self, webhook_payload: dict) -> Optional[Dict[str, Any]]:
        """
        Returns the last user message with its type and content.
        """

        messages = extract_whatsapp_user_messages(webhook_payload)

        if not messages:
            return None

        msg = messages[-1]
        msg_type = msg.get("type")

        if msg_type == "text":
            content = msg.get("text")

        elif msg_type == "audio":
            content = {
                "audio_id": msg.get("audio_id"),
                "mime_type": msg.get("mime_type")
            }

        elif msg_type == "image":
            content = {
                "image_id": msg.get("image_id"),
                "mime_type": msg.get("mime_type")
            }

        else:
            content = None

        return {
            "from": msg.get("from"),
            "type": msg_type,
            "content": content,
            "timestamp": msg.get("timestamp")
        }
    
    async def download_audio_from_url(self, audio_url: str, output_path: str = None) -> Optional[bytes]:
        """
            Télécharge l'audio depuis l'URL fournie par WAWP.
            L'URL est au format: http://localhost:3000/api/files/{message_id}.oga
        """
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                logger.info(f"Downloading audio from: {audio_url}")
                response = await client.get(audio_url)
                response.raise_for_status()
                
                audio_bytes = response.content
                
                # Sauvegarder si un chemin est fourni
                if output_path:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(audio_bytes)
                    logger.info(f"Audio saved to {output_path}")
                
                return audio_bytes
                
            except httpx.HTTPStatusError as e:
                logger.error(
                    f"HTTP error downloading audio {e.response.status_code}: {e.response.text}"
                )
                return None
                
            except Exception as e:
                logger.exception("Unexpected error downloading audio")
                return None